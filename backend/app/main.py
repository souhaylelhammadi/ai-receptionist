from fastapi import FastAPI

app = FastAPI(
    title="AI Receptionist API",
    description="API backend pour la plateforme AI Receptionist SaaS",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    """
    Endpoint simple pour vérifier que le serveur backend est en ligne.
    Utilisé plus tard par Docker/monitoring pour surveiller l'API.
    """
    return {"status": "ok"}