



import dropbox


token = 'sl.BGuEMeRaRu_huHEj2KLEOB1XpQ7uYHfdpGnSMuU5w1_uj8lIxzTsLPZNfe6i1SWqDYT0-6o77ucf6WWl9bVQtm_dCYWNBKwYx717RCOI5bXkvwTy36-zVfPH7fK_TCHXNni1p_5Br18'

if __name__ == '__main__':

    dbx = dropbox.Dropbox(token)
    print(dbx.files_list_folder(''))

