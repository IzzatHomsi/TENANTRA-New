from app.utils.email import send_email_alert
from jinja2 import Template
import os

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "../email_templates/alert_email.html")

def render_template(module_name, agent_name, timestamp):
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = Template(f.read())
        return template.render(
            module_name=module_name,
            agent_name=agent_name,
            timestamp=timestamp
        )

def send_compliance_failure_alert(user_email: str, module_name: str, agent_name: str, timestamp: str):
    subject = f"Compliance Alert - {module_name} failed"
    html = render_template(module_name, agent_name, timestamp)
    return send_email_alert(user_email, subject, html)
