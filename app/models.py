from app import db

class Payment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	date = db.Column(db.DateTime, index=True)
	desc = db.Column(db.String(120))
	amount = db.Column(db.Float)
	balance = db.Column(db.Float)
	category = db.Column(db.String(64), index=True)

	def __repr__(self):
		return '<User {}, {}, {}, {}>'.format(self.id, self.date, self.desc, self.category)

	def serialize(self):
		return {
		'id': self.id,
		'date': self.date,
		'desc': self.desc,
		'amount': self.amount,
		'balance': self.balance,
		'category': self.category}