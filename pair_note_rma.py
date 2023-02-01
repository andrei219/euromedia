

from app.db import session, WhIncomingRmaLine, CreditNoteLine


class RmaRegs:

	def __init__(self):
		self.rma_regs = [
			e for e in
			session.query(
				WhIncomingRmaLine.sn, WhIncomingRmaLine.item_id, WhIncomingRmaLine.condition,
				WhIncomingRmaLine.spec
			).limit(85)
		]

	def __eq__(self, other):
		return other == [(r.item_id, r.condition, r.spec) for r in self.rma_regs]

	def __iter__(self):
		return iter(self.rma_regs)


class NoteLines:

	def __init__(self):
		self.note_lines = [e for e in session.query(CreditNoteLine).limit(85)]

	def __eq__(self, other):
		return [(r.item_id, r.condition, r.spec) for r in self.note_lines] == other

	def __iter__(self):
		return iter(self.note_lines)

if __name__ == '__main__':

	rma_regs = RmaRegs()
	note_lines = NoteLines()

	if rma_regs != note_lines:
		raise ValueError('The things does not match, I will not do the pairing.')

	for rma_reg, line in zip(rma_regs, note_lines):
		line.sn = rma_reg.sn

	session.commit()





















