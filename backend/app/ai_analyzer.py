def generate_safer_alternative_with_ai(sql: str, risk_level: str, changed_tables: list, simulation_error: str) -> str:
    """
    Local deterministic function replacing the external API call.
    Creates a plain-English summary using verified simulation fields.
    """
    summary = f"Summary of Impact: This operation is classified as {risk_level} risk."
    
    if simulation_error:
        summary += f"\nSimulation failed with error: {simulation_error}"
    elif changed_tables:
        summary += f"\nTables modified: {', '.join(changed_tables)}"
    else:
        summary += "\nNo tracked tables were modified."
        
    summary += "\n\nRecommendation: Please ensure you have backups and use transactions for any destructive changes."
    
    return summary
