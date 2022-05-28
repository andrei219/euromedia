using EasySII;
using EasySII.Business;
using EasySII.Business.Batches;
using EasySII.Net;

using MySql.Data.MySqlClient;

using System.Diagnostics;

class DBConnect
{
    private MySqlConnection connection;
    private string server;
    private string database;
    private string uid;
    private string password;

    public DBConnect()
    {
        Initialize();
    }


    private void Initialize()
    {
        server = "localhost";
        database = "appdb";
        uid = "root";
        password = "hnq#4506";
        string connectionString;
        connectionString = "SERVER=" + server + ";" + "DATABASE=" + database + ";" + "UID=" + uid + ";" + "PASSWORD=" + password + ";";

        connection = new MySqlConnection(connectionString);
    }


    private bool OpenConnection()
    {
        try
        {
            connection.Open();
            return true;
        }
        catch (MySqlException ex)
        {
            //When handling errors, you can your application's response based 
            //on the error number.
            //The two most common error numbers when connecting are as follows:
            //0: Cannot connect to server.
            //1045: Invalid user name and/or password.
            switch (ex.Number)
            {
                case 0:
                    Console.WriteLine("Cannot connect to server.  Contact administrator");
                    break;

                case 1045:
                    Console.WriteLine("Invalid username/password, please try again");
                    break;
            }
            return false;
        }
    }

    //Close connection
    private bool CloseConnection()
    {
        try
        {
            connection.Close();
            return true;
        }
        catch (MySqlException ex)
        {
            Console.WriteLine(ex.Message);
            return false;
        }
    }
    public void Print_agent_names()
    {

        if (this.OpenConnection() == true)
        {
            MySqlCommand command = new MySqlCommand("SELECT * FROM PARTNERS", connection);

            MySqlDataReader dataReader = command.ExecuteReader();

            while (dataReader.Read())
                Console.WriteLine(dataReader["fiscal_name"]); 

            dataReader.Close();
            this.CloseConnection();

        }
    }
}
class Range
{
    public int from { get; set; }
    public int to { get; set; } 

    public Range(String astext)
    {
        String[] splitted = astext.Split('-'); 
        from = int.Parse(splitted[0]);
        to = int.Parse(splitted[1]);

    }

    public override string ToString()
    {
        return "Range(" + from.ToString() + ", " + to.ToString() + ")"; 
    }

}

class SII  
{
    private static bool SendInvoices(Dictionary<int, Range> series)
    {


        foreach (KeyValuePair<int, Range> pair in series)
        {
            Console.WriteLine("[" + pair.Key.ToString() + ", " + pair.Value.ToString() + "]");    
        }

        return true;
    }

    private static Dictionary<int, Range> ParseArgs(String[] args)
    {
        Dictionary<int, Range> ranges = new Dictionary<int, Range>();

        ranges.Add(int.Parse(args[0]), new Range(args[1]));
        ranges.Add(int.Parse(args[2]), new Range(args[3]));
        ranges.Add(int.Parse(args[4]), new Range(args[5]));
        ranges.Add(int.Parse(args[6]), new Range(args[7]));
        ranges.Add(int.Parse(args[8]), new Range(args[9]));
        ranges.Add(int.Parse(args[10]), new Range(args[11]));

        return ranges; 

    }


    private static void test_serie1()
    {
        Party titular = new()
        {
            TaxIdentificationNumber = "B98815608",
            PartyName = "Euromedia Investment Group, S.L."
        };


        // Lote de factura emitidas a enviar la AEAT al SII
        var loteFacturasEmitidas = new Batch(BatchActionKeys.LR, BatchActionPrefixes.SuministroLR, BatchTypes.FacturasEmitidas)
        {
            Titular = titular,
            CommunicationType = CommunicationType.A0
        };
        Party emisor = titular;

        Party p = new Party();

        ARInvoice facturaEnviadaPrimera = new()
        {
            IssueDate = new DateTime(2022, 5, 23),
            SellerParty = emisor,
            BuyerParty = new Party()
            {
                TaxIdentificationNumber = "B01611508",
                PartyName = "Microfix Labs, S.L."
            },
            
            CountryCode = "ES",

            InvoiceNumber = "1-000888",
            InvoiceType = InvoiceType.F1,
            ClaveRegimenEspecialOTrascendencia = ClaveRegimenEspecialOTrascendencia.RegimenComun,
            GrossAmount = 34375.39m,
            InvoiceText = "Operacion Nacional de venta de móviles, accesorios u otros aparatos electrónicos.",
             
        };

        facturaEnviadaPrimera.AddTaxOtuput(21m, 28359.83m, 5955.56m);
        facturaEnviadaPrimera.AddTaxOtuput(-(int)CausaExencion.E6, 60m, 0m);
        
        loteFacturasEmitidas.BatchItems.Add(facturaEnviadaPrimera);

        string response = BatchDispatcher.SendSiiLote(loteFacturasEmitidas);

        foreach (var factura in loteFacturasEmitidas.BatchItems)
        {
            string msg = "";
            if (factura.Status == "Correcto" || factura.Status == "AceptadoConErrores")
                msg = $"El estado del envío es: {factura.Status} y el código CSV: {factura.CSV}";
            else
                msg = $"El estado del envío es: {factura.Status}, error: {factura.ErrorCode} '{factura.ErrorMessage}'";

            // Continuar según resultado...

        }
    }

    private static void test_serie3()
    {
        Party titular = new()
        {
            TaxIdentificationNumber = "B98815608",
            PartyName = "Euromedia Investment Group, S.L."
        };

        // Lote de factura emitidas a enviar la AEAT al SII
        var loteFacturasEmitidas = new Batch(BatchActionKeys.LR, BatchActionPrefixes.SuministroLR, BatchTypes.FacturasEmitidas)
        {
            Titular = titular,
            CommunicationType = CommunicationType.A0
        };
        
        Party comprador = titular;

        Party emisor = titular;


        DateTime date = new DateTime(2022, 5, 23); 

        ARInvoice facturaEnviadaPrimera = new()
        {
            IssueDate = date, 
            OperationIssueDate = date, 
            SellerParty = emisor,

            CountryCode = "SM",

            BuyerParty = new Party()
            {
                TaxIdentificationNumber = "COESM04046",
                PartyName = "Datatrade, SPA"
            },

            InvoiceNumber = "3-00055",
            InvoiceType = InvoiceType.F1,
            ClaveRegimenEspecialOTrascendencia = ClaveRegimenEspecialOTrascendencia.ExportacionREAGYP,
            GrossAmount = 2000m,
            InvoiceText = "Exportación: Venta de móviles, accesorios u otros aparatos electrónicos.",
            IDOtroType = IDOtroType.DocOficialPaisResidencia,
        };


        facturaEnviadaPrimera.AddTaxOtuput(-(int)CausaExencion.E2, 2000m, 0m);

        loteFacturasEmitidas.BatchItems.Add(facturaEnviadaPrimera);

        string response = BatchDispatcher.SendSiiLote(loteFacturasEmitidas);

        foreach (var factura in loteFacturasEmitidas.BatchItems)
        {
            string msg = "";
            if (factura.Status == "Correcto" || factura.Status == "AceptadoConErrores")
                msg = $"El estado del envío es: {factura.Status} y el código CSV: {factura.CSV}";
            else
                msg = $"El estado del envío es: {factura.Status}, error: {factura.ErrorCode} '{factura.ErrorMessage}'";

            // Continuar según resultado...

        }
    }

    private static void test_serie2()
    {
        Party titular = new()
        {
            TaxIdentificationNumber = "B98815608",
            PartyName = "Euromedia Investment Group, S.L."
        };

        // Lote de factura emitidas a enviar la AEAT al SII
        var loteFacturasEmitidas = new Batch(BatchActionKeys.LR, BatchActionPrefixes.SuministroLR, BatchTypes.FacturasEmitidas)
        {
            Titular = titular,
            CommunicationType = CommunicationType.A0
        };

        Party emisor = titular;

        ARInvoice facturaEnviadaPrimera = new()
        {
            IssueDate = new DateTime(2022, 4, 20),
            SellerParty = emisor,

            BuyerParty = new Party()
            {
                TaxIdentificationNumber = "J93698819",
                PartyName = "Touchphone, S.C."
            },

            CountryCode = "ES",

            InvoiceNumber = "2-000198",
            InvoiceType = InvoiceType.F1,
            ClaveRegimenEspecialOTrascendencia = ClaveRegimenEspecialOTrascendencia.RegimenComun,
            GrossAmount = 25290.75m,
            InvoiceText = "Operacion Nacional con ISP de venta de móviles,acccesorios     q w            u otros aparatos electrónicos."
            
        };


        facturaEnviadaPrimera.AddTaxOtuput(21m, 410m, 86.10m);

        loteFacturasEmitidas.BatchItems.Add(facturaEnviadaPrimera);

        string response = BatchDispatcher.SendSiiLote(loteFacturasEmitidas);

        foreach (var factura in loteFacturasEmitidas.BatchItems)
        {
            string msg = "";
            if (factura.Status == "Correcto" || factura.Status == "AceptadoConErrores")
                msg = $"El estado del envío es: {factura.Status} y el código CSV: {factura.CSV}";
            else
                msg = $"El estado del envío es: {factura.Status}, error: {factura.ErrorCode} '{factura.ErrorMessage}'";

            // Continuar según resultado...

        }

    }
    private static void test_serie4()
    {

        // Exportacion paieses europeos.
        // tax siempre 0 
        Party titular = new()
        {
            TaxIdentificationNumber = "B98815608",
            PartyName = "Euromedia Investment Group, S.L."
        };

        // Lote de factura emitidas a enviar la AEAT al SII
        var loteFacturasEmitidas = new Batch(BatchActionKeys.LR, BatchActionPrefixes.SuministroLR, BatchTypes.FacturasEmitidas)
        {
            Titular = titular,
            CommunicationType = CommunicationType.A0
        };

        Party emisor = titular;

        ARInvoice facturaEnviadaPrimera = new()
        {
            IssueDate = new DateTime(2022, 4, 20),
            OperationIssueDate = new DateTime(2022, 4, 20),
            SellerParty = emisor,
            IDOtroType = IDOtroType.NifIva, 
            
            BuyerParty = new Party()
            {
                TaxIdentificationNumber = "BG205419545",
                PartyName = "AT Capital LTD."
            },

            CountryCode = "BG",

            InvoiceNumber = "4-000248",
            InvoiceType = InvoiceType.F1,
            ClaveRegimenEspecialOTrascendencia = ClaveRegimenEspecialOTrascendencia.RegimenComun,
            GrossAmount = 124260m,
            InvoiceText = "Operacion Intracomunitaria de venta de móviles, accesorios u otros aparatos electrónicos.", 
            
        };

        
        facturaEnviadaPrimera.AddTaxOtuput(-(int) CausaExencion.E5, 124260m, 0m);

        loteFacturasEmitidas.BatchItems.Add(facturaEnviadaPrimera);

        string response = BatchDispatcher.SendSiiLote(loteFacturasEmitidas);

        foreach (var factura in loteFacturasEmitidas.BatchItems)
        {
            string msg = "";
            if (factura.Status == "Correcto" || factura.Status == "AceptadoConErrores")
                msg = $"El estado del envío es: {factura.Status} y el código CSV: {factura.CSV}";
            else
                msg = $"El estado del envío es: {factura.Status}, error: {factura.ErrorCode} '{factura.ErrorMessage}'";

            // Continuar según resultado...

        }
    }

    private static void test_serie5()
    {
        Party titular = new()
        {
            TaxIdentificationNumber = "B98815608",
            PartyName = "Euromedia Investment Group, S.L."
        };

        // Lote de factura emitidas a enviar la AEAT al SII
        var loteFacturasEmitidas = new Batch(BatchActionKeys.LR, BatchActionPrefixes.SuministroLR, BatchTypes.FacturasEmitidas)
        {
            Titular = titular,
            CommunicationType = CommunicationType.A0
        };

        Party emisor = titular;

        ARInvoice facturaEnviadaPrimera = new()
        {
            IssueDate = new DateTime(2022, 4, 20),
            OperationIssueDate = new DateTime(2022, 4, 20), 
            SellerParty = emisor,

            BuyerParty = new Party()
            {
                TaxIdentificationNumber = "J93698819",
                PartyName = "Touchphone, S.C."
            },

            CountryCode = "ES",
            
            
            InvoiceNumber = "5-000999",
            InvoiceType = InvoiceType.F1,
            ClaveRegimenEspecialOTrascendencia = ClaveRegimenEspecialOTrascendencia.EspecialBienesUsados,
            GrossAmount = 562.42m,
            InvoiceText = "Operacion Nacional con REBU de venta de móviles, accesorios u otros aparatos electrónicos."
            

        };

        facturaEnviadaPrimera.AddTaxOtuput(-(int) CausaExencion.E6, 60m, 0m);
        facturaEnviadaPrimera.AddTaxOtuput(21m, 2, 0.42m);

        loteFacturasEmitidas.BatchItems.Add(facturaEnviadaPrimera);

        string response = BatchDispatcher.SendSiiLote(loteFacturasEmitidas);

        foreach (var factura in loteFacturasEmitidas.BatchItems)
        {
            string msg = "";
            if (factura.Status == "Correcto" || factura.Status == "AceptadoConErrores")
                msg = $"El estado del envío es: {factura.Status} y el código CSV: {factura.CSV}";
            else
                msg = $"El estado del envío es: {factura.Status}, error: {factura.ErrorCode} '{factura.ErrorMessage}'";

            // Continuar según resultado...

        }

    }
   
    public static void Main(String[] args) {

        String json_file_path = args[0];
        


    }
}

