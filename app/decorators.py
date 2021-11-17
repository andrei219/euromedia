

import db 

from PyQt5.QtWidgets import QMessageBox

def ask_save(fn):
    
    def decorator(self, event):
        if db.session.dirty:
            if QMessageBox.question(
                self,
                'Save-changes', 
                'Save changes?'
            ) == QMessageBox.Yes:
                db.session.commit()
            else:
                db.session.rollback() 
            fn(self, event)
        else:
            print('session is not dirty')
    
    return decorator
