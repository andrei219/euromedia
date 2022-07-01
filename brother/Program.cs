// See https://aka.ms/new-console-template for more information
using bpac;
using System.Runtime.InteropServices; 

class Printer
{

    public void Print(String path, String expedition_id, String date, String pi, String box, String boxid)
    {

            Document document = new();

            document.Open(path);

            document.SetPrinter("Brother QL-700", true);

            document.GetObject("Expedition_ID").Text = expedition_id;
            document.GetObject("Date").Text = date;
            document.GetObject("PI").Text = pi;
            document.GetObject("Box").Text = box;
            document.GetObject("Box_ID").Text = boxid;

            document.StartPrint("", PrintOptionConstants.bpoDefault);
            document.PrintOut(1, PrintOptionConstants.bpoDefault);
            document.EndPrint();
            document.Close();


    }

    public static void Main(String[] args)
    {
        string path = @"..\..\..\..\lbxs\Expedition Label.lbx";
        Printer printer = new();
        Console.WriteLine("Args: " + args.ToString()); 
        // printer.Print(path, "", "", "", "", "");
    }
}

