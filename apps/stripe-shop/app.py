import os
import stripe
from flask import Flask, redirect, request

stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
app = Flask(__name__)

@app.route("/")
def index():
    return """<h1>Boutique PC-04-11-2026</h1>
<p>T-shirt : 20,00 EUR</p>
<form action="/checkout" method="POST"><button>Acheter</button></form>"""

@app.route("/checkout", methods=["POST"])
def checkout():
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "eur",
                "unit_amount": 2000,
                "product_data": {"name": "T-shirt"},
            },
            "quantity": 1,
        }],
        success_url=request.host_url + "success",
        cancel_url=request.host_url,
    )
    return redirect(session.url, code=303)

@app.route("/success")
def success():
    return "<h1>Paiement reçu, merci !</h1><a href='/'>Retour</a>"