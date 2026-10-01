from __future__ import annotations

from .config import (
	DEMO_MODE,
	GOOGLE_API_KEY,
	TIP_MODEL,
	WORKOUT_MODEL,
)


class GeminiServiceError(RuntimeError):
	pass


_client = None


def _get_client():
	global _client

	if _client is None:

		if not GOOGLE_API_KEY:
			raise GeminiServiceError(
				"GOOGLE_API_KEY is not configured. "
				"Add it to .env or enable DEMO_MODE=true."
			)

		# Lazy import means demo mode can run without the SDK.
		from google import genai

		_client = genai.Client(
			api_key=GOOGLE_API_KEY
		)

	return _client


def _clean(text: str | None) -> str:

	if not text:
		raise GeminiServiceError(
			"Gemini returned an empty response."
		)

	return text.strip()


def generate_workout(
	name: str,
	age: int,
	weight: float,
	goal: str,
	intensity: str
) -> str:

	if DEMO_MODE:
		return demo_workout(
			name,
			goal,
			intensity
		)

	prompt = f"""
You are FitBuddy, a careful fitness-plan assistant.

Create a practical 7-day workout plan.

User:

Name: {name}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Preferred intensity: {intensity}

Requirements:

1. Output exactly 7 days.
2. Label them Day 1 through Day 7.
3. Include a warm-up.
4. Include the main workout.
5. Include cooldown or recovery guidance.
6. Give exercises with sets/reps or duration.
7. Give rest periods where appropriate.
8. Match difficulty to the selected intensity.
9. Include at least one recovery/rest-focused day.
10. Do not prescribe drugs or unsafe challenges.
11. Do not make medical diagnoses.
12. Keep the plan easy to follow.

The result should be practical and structured.
"""

	try:

		response = _get_client().models.generate_content(
			model=WORKOUT_MODEL,
			contents=prompt
		)

		return _clean(
			response.text
		)

	except Exception as exc:

		raise GeminiServiceError(
			f"Workout generation failed: {exc}"
		) from exc


def generate_nutrition_tip(
	goal: str
) -> str:

	if DEMO_MODE:
		return demo_tip(goal)

	prompt = f"""
Give one concise and practical nutrition or recovery tip
for a fitness user whose goal is:

{goal}

Keep it under 120 words.

Avoid:

- medical claims
- extreme dieting
- unsafe recommendations

Give the user one simple action they can take today.
"""

	try:

		response = _get_client().models.generate_content(
			model=TIP_MODEL,
			contents=prompt
		)

		return _clean(
			response.text
		)

	except Exception as exc:

		raise GeminiServiceError(
			f"Nutrition tip generation failed: {exc}"
		) from exc


def update_workout(
	original_plan: str,
	feedback: str,
	goal: str,
	intensity: str
) -> str:

	if DEMO_MODE:
		return demo_update(
			original_plan,
			feedback
		)

	prompt = f"""
You are revising an existing FitBuddy workout plan.

Fitness goal:
{goal}

Preferred intensity:
{intensity}

Original plan:

{original_plan}

User feedback:

{feedback}

Return a COMPLETE revised 7-day workout plan.

Do not return only a list of changes.

Requirements:

- Day 1 through Day 7
- Warm-up
- Main workout
- Sets/reps or duration
- Rest periods where useful
- Cooldown/recovery
- Apply the user's feedback intelligently
- Keep the plan realistic
- Keep the plan safe
"""

	try:

		response = _get_client().models.generate_content(
			model=WORKOUT_MODEL,
			contents=prompt
		)

		return _clean(
			response.text
		)

	except Exception as exc:

		raise GeminiServiceError(
			f"Workout update failed: {exc}"
		) from exc


# ---------------------------------------------------------
# DEMO MODE
# ---------------------------------------------------------

def demo_workout(
	name: str,
	goal: str,
	intensity: str
) -> str:

	level = {
		"low": "2 sets",
		"medium": "3 sets",
		"high": "4 sets"
	}[intensity]

	focus = {
		"weight loss":
			"full-body conditioning",

		"muscle gain":
			"strength and hypertrophy",

		"general wellness":
			"balanced fitness",

		"flexibility":
			"mobility and flexibility",
	}[goal]

	days = [

		(
			"Full Body",
			"Squats, push-ups, rows, lunges",
			"20-30 min"
		),

		(
			"Cardio",
			"Brisk walk or cycling + core",
			"25-35 min"
		),

		(
			"Upper Body",
			"Push-ups, rows, shoulder press, curls",
			"30 min"
		),

		(
			"Recovery",
			"Easy walking + mobility",
			"20-30 min"
		),

		(
			"Lower Body",
			"Squats, split squats, glute bridges, calf raises",
			"30 min"
		),

		(
			"Conditioning",
			"Intervals + plank variations",
			"25-35 min"
		),

		(
			"Rest",
			"Gentle stretching and relaxed walking",
			"15-25 min"
		),
	]

	sections = [

		f"""
FITBUDDY DEMO PLAN FOR {name.upper()}

Goal: {goal}
Intensity: {intensity}
Focus: {focus}
"""
	]

	for i, (
		title,
		exercises,
		duration
	) in enumerate(days, start=1):

		sections.append(
			f"""
Day {i} — {title}

Warm-up:
5-10 minutes of easy movement.

Main:
{exercises}.

Use {level} for strength movements.

Rest:
60-90 seconds between sets.

Duration:
{duration}.

Cooldown:
5 minutes of easy movement and gentle stretching.
"""
		)

	return "\n".join(sections)


def demo_tip(goal: str) -> str:

	tips = {

		"weight loss":
			"Prioritize filling meals built around vegetables, "
			"a protein source, and a sensible portion of carbohydrates. "
			"Keep hydration consistent and avoid crash dieting.",

		"muscle gain":
			"Include a protein-rich food in each main meal and eat "
			"enough total food to support training. Good options include "
			"eggs, dairy, fish, chicken, soy, beans, and lentils.",

		"general wellness":
			"Build a simple routine: regular meals, adequate water, "
			"fruits and vegetables, protein-rich foods, and enough sleep.",

		"flexibility":
			"Hydrate normally and include protein-rich foods plus "
			"fruits and vegetables. Recovery improves when mobility "
			"work is paired with adequate sleep and regular meals.",
	}

	return tips[goal]


def demo_update(
	original_plan: str,
	feedback: str
) -> str:

	return (
		original_plan
		+
		"\n\n--- DEMO UPDATE ---\n"
		+
		f"Applied user feedback: {feedback}\n"
		+
		"In a real Gemini run, this section would be "
		"replaced by a complete AI-generated revised "
		"7-day plan."
	)