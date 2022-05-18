



import dropbox


token = 'sl.BHzhJzAvPI5O13IdwM2idciJVuAFxHbC6skgY-wlTxL4PO8NaHeVPhX-qaSQ9iNrTl6pF-FmZrhbja7AMB25uovH27J94Fs7NHFU8WqqreACGtc6hPO8gnvyvUHAjpkXUF_fkMm3Muc'

if __name__ == '__main__':

    dbx = dropbox.Dropbox(token)
    print(dbx.files_list_folder(''))

