from pathlib import Path

from fastapi import (
	APIRouter,
	Depends,
	Form,
	HTTPException,
	Request,
)

from fastapi.responses import (
	HTMLResponse,
	RedirectResponse,
)

from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from .config import ADMIN_KEY

from .database import get_db

from .gemini_service import (
	GeminiServiceError,
	generate_nutrition_tip,
	generate_workout,
	update_workout,
)

from .schemas import (
	FeedbackRequest,
	UserInput,
)

from .services import (
	create_or_update_user,
	delete_user,
	get_all_users,
	get_user,
	save_plan,
	update_plan,
)


router = APIRouter()

templates = Jinja2Templates(
	directory=str(Path(__file__).resolve().parent.parent / "templates")
)


def render_error(
	request: Request,
	message: str,
	status_code: int = 400
):

	return templates.TemplateResponse(
		request=request,
		name="error.html",
		context={
			"message": message,
			"code": status_code,
		},
		status_code=status_code,
	)


def admin_authorized(
	key: str | None
) -> bool:

	return bool(key) and key == ADMIN_KEY


@router.get(
	"/",
	response_class=HTMLResponse
)
def home(
	request: Request
):

	return templates.TemplateResponse(
		request=request,
		name="index.html",
		context={}
	)


@router.get("/health")
def health():
	return {"status": "ok"}


@router.post(
	"/generate-workout",
	response_class=HTMLResponse
)
def generate_workout_route(
	request: Request,

	name: str = Form(...),

	user_id: str = Form(...),

	age: int = Form(...),

	weight: float = Form(...),

	goal: str = Form(...),

	intensity: str = Form(...),

	db: Session = Depends(get_db),
):

	try:

		data = UserInput(
			name=name.strip(),
			user_id=user_id.strip(),
			age=age,
			weight=weight,
			goal=goal,
			intensity=intensity,
		)

	except Exception as exc:

		return render_error(
			request,
			f"Invalid input: {exc}",
			422
		)

	try:

		workout_plan = generate_workout(
			data.name,
			data.age,
			data.weight,
			data.goal,
			data.intensity
		)

		nutrition_tip = generate_nutrition_tip(
			data.goal
		)

		user = create_or_update_user(
			db,
			data
		)

		save_plan(
			db,
			user,
			workout_plan,
			nutrition_tip
		)

		user = get_user(
			db,
			data.user_id
		)

		return templates.TemplateResponse(
			request=request,
			name="result.html",
			context={
				"user": user,
				"plan": user.plan,
				"message": None
			}
		)

	except GeminiServiceError as exc:

		db.rollback()

		return render_error(
			request,
			str(exc),
			503
		)

	except Exception as exc:

		db.rollback()

		return render_error(
			request,
			f"Unexpected error: {exc}",
			500
		)


@router.post(
	"/submit-feedback",
	response_class=HTMLResponse
)
def submit_feedback_route(
	request: Request,

	user_id: str = Form(...),

	feedback: str = Form(...),

	db: Session = Depends(get_db),
):

	try:

		data = FeedbackRequest(
			user_id=user_id.strip(),
			feedback=feedback.strip()
		)

	except Exception as exc:

		return render_error(
			request,
			f"Invalid feedback: {exc}",
			422
		)

	user = get_user(
		db,
		data.user_id
	)

	if user is None or user.plan is None:

		return render_error(
			request,
			"No saved plan was found for that User ID.",
			404
		)

	try:

		revised = update_workout(
			user.plan.original_plan,
			data.feedback,
			user.goal,
			user.intensity
		)

		nutrition_tip = generate_nutrition_tip(
			user.goal
		)

		update_plan(
			db,
			user,
			revised,
			data.feedback,
			nutrition_tip
		)

		user = get_user(
			db,
			data.user_id
		)

		return templates.TemplateResponse(
			request=request,
			name="result.html",
			context={
				"user": user,
				"plan": user.plan,
				"message": "Your plan was updated successfully."
			}
		)

	except GeminiServiceError as exc:

		db.rollback()

		return render_error(
			request,
			str(exc),
			503
		)

	except Exception as exc:

		db.rollback()

		return render_error(
			request,
			f"Unexpected error: {exc}",
			500
		)


@router.get(
	"/view-all-users",
	response_class=HTMLResponse
)
def view_all_users(
	request: Request,
	key: str | None = None,
	db: Session = Depends(get_db)
):

	if not admin_authorized(key):

		return render_error(
			request,
			"Unauthorized. Open this page with the correct admin key.",
			401
		)

	users = get_all_users(db)

	return templates.TemplateResponse(
		request=request,
		name="all_users.html",
		context={
			"users": users,
			"key": key
		}
	)


@router.post(
	"/admin/delete/{user_id}"
)
def delete_user_route(
	user_id: str,
	key: str = Form(...),
	db: Session = Depends(get_db)
):

	if not admin_authorized(key):

		raise HTTPException(
			status_code=401,
			detail="Unauthorized"
		)

	user = get_user(
		db,
		user_id
	)

	if user is None:

		raise HTTPException(
			status_code=404,
			detail="User not found"
		)

	delete_user(
		db,
		user
	)

	return RedirectResponse(
		url=f"/view-all-users?key={key}",
		status_code=303
	)


@router.get(
	"/api/users"
)
def api_users(
	key: str | None = None,
	db: Session = Depends(get_db)
):

	if not admin_authorized(key):

		raise HTTPException(
			status_code=401,
			detail="Unauthorized"
		)

	users = get_all_users(db)

	return [
		{
			"user_id": user.user_id,
			"name": user.name,
			"age": user.age,
			"weight": user.weight,
			"goal": user.goal,
			"intensity": user.intensity,

			"original_plan":
				user.plan.original_plan
				if user.plan
				else None,

			"updated_plan":
				user.plan.updated_plan
				if user.plan
				else None,

			"last_feedback":
				user.plan.last_feedback
				if user.plan
				else None,
		}

		for user in users
	]


@router.get(
	"/api/users/{user_id}"
)
def api_user(
	user_id: str,

	key: str | None = None,

	db: Session = Depends(get_db)
):

	if not admin_authorized(key):

		raise HTTPException(
			status_code=401,
			detail="Unauthorized"
		)

	user = get_user(
		db,
		user_id
	)

	if user is None:

		raise HTTPException(
			status_code=404,
			detail="User not found"
		)

	return {

		"user_id": user.user_id,

		"name": user.name,

		"age": user.age,

		"weight": user.weight,

		"goal": user.goal,

		"intensity": user.intensity,

		"original_plan":
			user.plan.original_plan
			if user.plan
			else None,

		"updated_plan":
			user.plan.updated_plan
			if user.plan
			else None,

		"nutrition_tip":
			user.plan.nutrition_tip
			if user.plan
			else None,

		"last_feedback":
			user.plan.last_feedback
			if user.plan
			else None,
	}
