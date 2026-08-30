import os

from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI


def _local_summary(
    sql: str,
    risk_level: str,
    changed_tables: list,
    simulation_error: str | None,
) -> str:
    summary = f"Summary of Impact: This operation is classified as {risk_level} risk."

    if simulation_error:
        summary += f"\nSimulation failed with error: {simulation_error}"
    elif changed_tables:
        summary += f"\nTables modified: {', '.join(changed_tables)}"
    else:
        summary += "\nNo tracked tables were modified."

    summary += (
        "\n\nRecommendation: Use backups and transactions for destructive changes. "
        "ProofGuard only simulates this action in an isolated database clone."
    )
    return summary


def generate_safer_alternative(
    sql: str,
    risk_level: str,
    changed_tables: list,
    simulation_error: str | None,
) -> str:
    """Return an LLM explanation when available; otherwise return safe local text."""
    fallback = _local_summary(sql, risk_level, changed_tables, simulation_error)

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return fallback

    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

        response = client.chat.completions.create(
            model=os.getenv("OPENROUTER_MODEL", "openrouter/auto"),
            temperature=0,
            max_tokens=160,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are ProofGuard, a database safety assistant. "
                        "Explain the SQL risk and provide a safer alternative in plain language. "
                        "Never claim that SQL was executed. "
                        "The query was only simulated in an isolated database clone. "
                        "Keep the response under 90 words."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"SQL: {sql}\n"
                        f"Deterministic risk level: {risk_level}\n"
                        f"Changed tables: {', '.join(changed_tables) or 'none'}\n"
                        f"Simulation error: {simulation_error or 'none'}"
                    ),
                },
            ],
        )

        text = (response.choices[0].message.content or "").strip()
        return text or fallback

    except Exception:
        return fallback 
 
def generate_safer_alternative_with_ai(
    sql: str,
    risk_level: str,
    changed_tables: list,
    simulation_error: str | None,
) -> str:
    """Backward-compatible name used by the existing safety engine."""
    return generate_safer_alternative(
        sql=sql,
        risk_level=risk_level,
        changed_tables=changed_tables,
        simulation_error=simulation_error,
    )
