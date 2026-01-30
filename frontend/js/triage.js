import { loadRules } from "./rules.js";

function opEval(a, op, b) {
  if (a == null) return false;
  if (op === "==") return a === b;
  if (op === "<=") return a <= b;
  if (op === ">=") return a >= b;
  if (op === "<") return a < b;
  if (op === ">") return a > b;
  return false;
}

function evalRule(conditions, ctx) {
  // conditions with optional "logic" chaining (defaults AND)
  let acc = true;
  let pendingLogic = "AND";
  for (const c of conditions) {
    const v = ctx[c.field];
    const ok = opEval(v, c.op, c.value);
    const logic = c.logic || "AND";
    if (pendingLogic === "AND") acc = acc && ok;
    else acc = acc || ok;
    pendingLogic = logic;
  }
  return acc;
}

function bandScore(bands, value) {
  for (const b of bands) {
    const minOk = (b.min == null) ? true : value >= b.min;
    const maxOk = (b.max == null) ? true : value <= b.max;
    if (minOk && maxOk) return b.score;
  }
  return 100;
}

function dateAddDays(d, days) {
  const x = new Date(d);
  x.setDate(x.getDate() + days);
  return x.toISOString().slice(0,10);
}

export async function computeDerived(input) {
  const rules = await loadRules();

  // normalize context (compute averages + bmi)
  const sbp_avg = (input.sbp1!=null && input.sbp2!=null) ? Math.round((input.sbp1+input.sbp2)/2) : null;
  const dbp_avg = (input.dbp1!=null && input.dbp2!=null) ? Math.round((input.dbp1+input.dbp2)/2) : null;
  const bmi = (input.weight && input.height) ? +(input.weight/(input.height*input.height)).toFixed(2) : null;

  const ctx = { ...input, sbp_avg, dbp_avg, bmi };

  // triage: first critical then moderate else green
  let rag = rules.triage.default.rag;
  let next_step = rules.triage.default.next_step;
  const flags = [];

  for (const r of rules.triage.critical) {
    if (evalRule(r.conditions, ctx)) {
      rag = r.rag; next_step = r.next_step; flags.push(r.id);
      break;
    }
  }
  if (rag === "GREEN") {
    for (const r of rules.triage.moderate) {
      if (evalRule(r.conditions, ctx)) {
        rag = r.rag; next_step = r.next_step; flags.push(r.id);
      }
    }
  }

  // domain scoring
  const domain_scores = {};
  for (const [domain, dcfg] of Object.entries(rules.scoring.domains)) {
    let sumW = 0, sum = 0;
    for (const comp of dcfg.components) {
      let s = 100;
      if (comp.bands) s = bandScore(comp.bands, ctx[comp.field]);
      else if (comp.bands_by_type) {
        const t = ctx.glucose_type;
        const v = ctx.glucose_value;
        if (t && v != null) s = bandScore(comp.bands_by_type[t]||[], v);
      } else if (comp.symptom_scores) {
        s = comp.symptom_scores[ctx[comp.field] || "none"] ?? 100;
      }
      sum += s * comp.weight;
      sumW += comp.weight;
    }
    domain_scores[domain] = sumW ? Math.round(sum / sumW) : 100;
  }

  // overall score
  let overall = 0, wsum = 0;
  for (const [domain, w] of Object.entries(rules.scoring.overall_weights)) {
    overall += (domain_scores[domain] ?? 100) * w;
    wsum += w;
  }
  overall = wsum ? Math.round(overall / wsum) : 100;
  if (rag === "RED") overall = Math.min(overall, rules.scoring.red_score_cap);

  // due engine
  const age = input.age_years ?? null;
  const base = (age != null && age >= 30) ? rules.due_engine.base_intervals_days.age_30_plus : rules.due_engine.base_intervals_days.under_30;

  let interval = base;
  const ragOverride = rules.due_engine.rag_overrides_days[rag];
  if (ragOverride != null) interval = Math.min(interval, ragOverride);

  for (const f of flags) {
    const ov = rules.due_engine.flag_overrides_days[f];
    if (ov != null) interval = Math.min(interval, ov);
  }

  interval = Math.max(rules.due_engine.min_interval_days, Math.min(rules.due_engine.max_interval_days, interval));
  const next_due_date = dateAddDays(new Date(), interval);

  return { rag, flags, next_step, domain_scores, overall_score: overall, next_due_date };
}
