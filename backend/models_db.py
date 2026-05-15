import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, Boolean, Date, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


def new_uuid() -> str:
    return str(uuid.uuid4())


class Athlete(Base):
    __tablename__ = "athletes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    supabase_user_id: Mapped[str | None] = mapped_column(String, unique=True, nullable=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    height_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    plans: Mapped[list["Plan"]] = relationship(back_populates="athlete")


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    athlete_id: Mapped[str] = mapped_column(String, ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False)
    sport_type: Mapped[str] = mapped_column(String, nullable=False)
    race_date: Mapped[str] = mapped_column(Date, nullable=False)
    target_race_time_hours: Mapped[float] = mapped_column(Float, nullable=False)
    start_preference: Mapped[str] = mapped_column(String, nullable=False)
    preferred_start_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    long_sessions: Mapped[list] = mapped_column(JSON, nullable=False)
    carb_tolerance: Mapped[str] = mapped_column(String, nullable=False)
    gi_history: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[str] = mapped_column(Date, nullable=False)
    end_date: Mapped[str] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    athlete: Mapped["Athlete"] = relationship(back_populates="plans")
    weeks: Mapped[list["Week"]] = relationship(back_populates="plan", cascade="all, delete", passive_deletes=True)


class Week(Base):
    __tablename__ = "weeks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    plan_id: Mapped[str] = mapped_column(String, ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[str] = mapped_column(Date, nullable=False)
    end_date: Mapped[str] = mapped_column(Date, nullable=False)
    target_carbs_g_per_hour: Mapped[float] = mapped_column(Float, nullable=False)
    ratio_phase: Mapped[int] = mapped_column(Integer, nullable=False)
    is_consolidation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    plan: Mapped["Plan"] = relationship(back_populates="weeks")
    sessions: Mapped[list["Session"]] = relationship(back_populates="week", cascade="all, delete", passive_deletes=True)


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    week_id: Mapped[str] = mapped_column(String, ForeignKey("weeks.id", ondelete="CASCADE"), nullable=False)
    session_number: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_option: Mapped[str] = mapped_column(String, nullable=False)
    n_fueling_windows: Mapped[int] = mapped_column(Integer, nullable=False)

    week: Mapped["Week"] = relationship(back_populates="sessions")
    fueling_windows: Mapped[list["FuelingWindow"]] = relationship(back_populates="session", cascade="all, delete", passive_deletes=True)
    feedback: Mapped[list["Feedback"]] = relationship(back_populates="session", cascade="all, delete", passive_deletes=True)


class ExtraSession(Base):
    """An unplanned session the athlete completed in addition to the planned ones."""
    __tablename__ = "extra_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    week_id: Mapped[str] = mapped_column(String, ForeignKey("weeks.id", ondelete="CASCADE"), nullable=False)
    duration_option: Mapped[str] = mapped_column(String, nullable=False)
    n_small_gels_consumed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    n_large_gels_consumed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    gi_scale: Mapped[int] = mapped_column(Integer, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Gel(Base):
    __tablename__ = "gels"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    size: Mapped[str] = mapped_column(String, nullable=False)
    carbs_g: Mapped[int] = mapped_column(Integer, nullable=False)
    glucose_pct: Mapped[float] = mapped_column(Float, nullable=False)
    fructose_pct: Mapped[float] = mapped_column(Float, nullable=False)
    ratio_phase: Mapped[int] = mapped_column(Integer, nullable=False)



class FuelingWindow(Base):
    __tablename__ = "fueling_windows"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    small_gel_id: Mapped[str | None] = mapped_column(String, ForeignKey("gels.id"), nullable=True)
    large_gel_id: Mapped[str | None] = mapped_column(String, ForeignKey("gels.id"), nullable=True)
    window_number: Mapped[int] = mapped_column(Integer, nullable=False)
    time_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    carbs_target_g: Mapped[float] = mapped_column(Float, nullable=False)
    carbs_actual_g: Mapped[float] = mapped_column(Float, nullable=False)
    n_small_gels: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    n_large_gels: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    session: Mapped["Session"] = relationship(back_populates="fueling_windows")
    small_gel: Mapped["Gel | None"] = relationship(foreign_keys=[small_gel_id])
    large_gel: Mapped["Gel | None"] = relationship(foreign_keys=[large_gel_id])


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="completed")  # completed / skipped
    consumed_vs_plan: Mapped[str | None] = mapped_column(String, nullable=True)  # less / as_planned / more
    consumed_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    gi_scale: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 0=none 1=mild 2=moderate 3=severe
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["Session"] = relationship(back_populates="feedback")
