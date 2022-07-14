
class SavingError(Exception):
    pass 

class FetchingError(Exception):
    pass 

class UpdatingError(Exception):
    pass 

class DeletingError(Exception):
    pass 

class DuplicateLine(Exception):
    pass 

class NoPartnerError(Exception):
    pass 

class SeriePresentError(Exception):
    pass 

class LineCompletedError(Exception):
    pass 

class NotExistingStockOutput(Exception):
    pass

class NotExistingStockInMask(Exception):
    pass

class AutomaticReceptionDeleteError(Exception):
    pass