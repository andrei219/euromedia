from python_dhl.service import DHLService


import Setting



service = DHLService(api_key=Setting.DHL_API_KEY, api_secret=Setting.DHL_API_SECRET,
                     account_number=Setting.DHL_ACCOUNT_EXPORT,
                     test_mode=True)


if __name__ == '__main__':



    import  win32print
    import win32api

    # currentprinter = win32print.GetDefaultPrinter()
    # win32api.ShellExecute(0, "print", 'PDFfile.pdf', '/d:"%s"' % currentprinter, ".", 0)

    for printer in win32print.EnumPrinters(3):
        print(printer)