"""initial

Revision ID: 0001_initial
Revises:
Create Date: 2026-01-30
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "villages",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("district", sa.String(120), nullable=True),
        sa.Column("state", sa.String(120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "households",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("village_id", sa.Integer, sa.ForeignKey("villages.id"), nullable=False),
        sa.Column("hamlet", sa.String(120)),
        sa.Column("address", sa.Text),
        sa.Column("head_name", sa.String(120)),
        sa.Column("phone", sa.String(32)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_households_village_updated", "households", ["village_id", "updated_at"])

    op.create_table(
        "people",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("household_id", sa.Integer, sa.ForeignKey("households.id"), nullable=False),
        sa.Column("village_id", sa.Integer, sa.ForeignKey("villages.id"), nullable=False),
        sa.Column("full_name", sa.String(160), nullable=False),
        sa.Column("sex", sa.String(16)),
        sa.Column("dob", sa.Date),
        sa.Column("phone", sa.String(32)),
        sa.Column("demographics_json", sa.JSON),
        sa.Column("risk_survey_json", sa.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_people_village_updated", "people", ["village_id", "updated_at"])

    op.create_table(
        "workers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(80), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("display_name", sa.String(120)),
        sa.Column("phone", sa.String(32)),
        sa.Column("assigned_villages_json", sa.JSON),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "camps",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("village_id", sa.Integer, sa.ForeignKey("villages.id"), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("start_time", sa.String(16)),
        sa.Column("end_time", sa.String(16)),
        sa.Column("address", sa.Text),
        sa.Column("landmark", sa.String(160)),
        sa.Column("lat", sa.Numeric(10, 7), nullable=False),
        sa.Column("lng", sa.Numeric(10, 7), nullable=False),
        sa.Column("contact_name", sa.String(120)),
        sa.Column("contact_phone", sa.String(32)),
        sa.Column("services_json", sa.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_camps_village_date", "camps", ["village_id", "date"])

    op.create_table(
        "totp_secrets",
        sa.Column("person_id", sa.Integer, sa.ForeignKey("people.id"), primary_key=True),
        sa.Column("secret_encrypted", sa.LargeBinary, nullable=False),
        sa.Column("provisioning_done", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("last_verified_timestep", sa.Integer, server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "encounters",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("person_id", sa.Integer, sa.ForeignKey("people.id"), nullable=False),
        sa.Column("camp_id", sa.Integer, sa.ForeignKey("camps.id")),
        sa.Column("started_by_worker_id", sa.Integer, sa.ForeignKey("workers.id"), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True)),
        sa.Column("submitted_at", sa.DateTime(timezone=True)),
        sa.Column("client_created_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "vitals",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("encounter_id", sa.Integer, sa.ForeignKey("encounters.id"), unique=True, nullable=False),
        sa.Column("sbp1", sa.Integer),
        sa.Column("dbp1", sa.Integer),
        sa.Column("sbp2", sa.Integer),
        sa.Column("dbp2", sa.Integer),
        sa.Column("sbp_avg", sa.Integer),
        sa.Column("dbp_avg", sa.Integer),
        sa.Column("hr", sa.Integer),
        sa.Column("spo2", sa.Integer),
        sa.Column("temp", sa.Numeric(4, 1)),
        sa.Column("weight", sa.Numeric(6, 2)),
        sa.Column("height", sa.Numeric(4, 2)),
        sa.Column("bmi", sa.Numeric(5, 2)),
        sa.Column("waist", sa.Numeric(6, 2)),
        sa.Column("symptoms_json", sa.JSON),
        sa.Column("risk_json", sa.JSON),
        sa.Column("consent", sa.Boolean, server_default=sa.text("true"), nullable=False),
    )

    op.create_table(
        "tests",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("encounter_id", sa.Integer, sa.ForeignKey("encounters.id"), unique=True, nullable=False),
        sa.Column("glucose_type", sa.String(16)),
        sa.Column("glucose_value", sa.Integer),
        sa.Column("hb", sa.Numeric(4, 1)),
        sa.Column("urine_dip_json", sa.JSON),
    )

    op.create_table(
        "derived_results",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("encounter_id", sa.Integer, sa.ForeignKey("encounters.id"), unique=True, nullable=False),
        sa.Column("rag", sa.String(8), nullable=False),
        sa.Column("flags_json", sa.JSON),
        sa.Column("next_step", sa.Text),
        sa.Column("followup_date", sa.Date),
        sa.Column("domain_scores_json", sa.JSON),
        sa.Column("overall_score", sa.Integer),
    )

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("person_id", sa.Integer, sa.ForeignKey("people.id"), nullable=False),
        sa.Column("encounter_id", sa.Integer, sa.ForeignKey("encounters.id")),
        sa.Column("type", sa.String(32), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("due_date", sa.Date),
        sa.Column("notes", sa.Text),
        sa.Column("created_by_worker_id", sa.Integer, sa.ForeignKey("workers.id"), nullable=False),
        sa.Column("closed_by_worker_id", sa.Integer, sa.ForeignKey("workers.id")),
        sa.Column("closed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "reminder_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("person_id", sa.Integer, sa.ForeignKey("people.id"), nullable=False),
        sa.Column("worker_id", sa.Integer, sa.ForeignKey("workers.id"), nullable=False),
        sa.Column("outcome", sa.String(32), nullable=False),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "inventory_items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("unit", sa.String(32)),
        sa.Column("quantity", sa.Integer, server_default="0", nullable=False),
        sa.Column("meta_json", sa.JSON),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "verification_tokens",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("encounter_id", sa.Integer, sa.ForeignKey("encounters.id"), nullable=False),
        sa.Column("token", sa.String(128), unique=True, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("actor_worker_id", sa.Integer, sa.ForeignKey("workers.id")),
        sa.Column("actor_person_id", sa.Integer, sa.ForeignKey("people.id")),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("entity", sa.String(64), nullable=False),
        sa.Column("entity_id", sa.String(64)),
        sa.Column("meta_json", sa.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

def downgrade():
    op.drop_table("audit_logs")
    op.drop_table("verification_tokens")
    op.drop_table("inventory_items")
    op.drop_table("reminder_logs")
    op.drop_table("tasks")
    op.drop_table("derived_results")
    op.drop_table("tests")
    op.drop_table("vitals")
    op.drop_table("encounters")
    op.drop_table("totp_secrets")
    op.drop_index("ix_camps_village_date", table_name="camps")
    op.drop_table("camps")
    op.drop_table("workers")
    op.drop_index("ix_people_village_updated", table_name="people")
    op.drop_table("people")
    op.drop_index("ix_households_village_updated", table_name="households")
    op.drop_table("households")
    op.drop_table("villages")
