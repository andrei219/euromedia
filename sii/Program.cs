
using EasySII; 
using EasySII.Business;
using EasySII.Business.Batches;
using EasySII.Xml.Sii; 
using EasySII.Net;
using EasySII.Xml; 

using System.Text.Json; 



class SIILine
{
    public int quantity { get; set; }
    public Decimal price { get; set; }  
    public int tax { get; set; }
    public bool is_stock { get; set;  }

    public override string ToString()
    {
        return "SIILine(" + this.quantity.ToString() + ", "+ this.price.ToString() + ", ..., )"; 
    }

}

class SIInvoice
{
    public String invoice_number { get; set;  }
    public String partner_name { get; set; }   
    public String partner_ident { get; set; }
    public String country_code { get; set;  }
    public String invoice_date { get; set;  }
    
    public bool ambos_tax { get; set; }

    public List<SIILine> lines { get; set; }


    public override string ToString()
    {
        return this.invoice_number + ", date=" + this.invoice_date.ToString(); 
    }

}

class SIIResponse
{

    public String invoice_number { get; set; }
    public String invoice_date { get; set; }
    public String invoice_status { get; set;  }

    public String message { get; set; }
}


class SII
{ 
    private static decimal Gross_amount(SIInvoice siinvoice)
    {
        Decimal subtotal = 0;
        Decimal tax = 0;
        Decimal taxaccum = 0;
        Decimal subtotalaccum = 0;
        foreach (SIILine line in siinvoice.lines)
        {
            subtotal = line.price * line.quantity;
            tax = subtotal * line.tax/100;

            subtotalaccum += subtotal; 
            taxaccum += tax;
        }

        return Math.Round(subtotalaccum + taxaccum, 2); 
    }

    private static DateTime get_date(String datestring)
    {
        String[] date_components = datestring.Split("-");
        int day = Int32.Parse(date_components[0]);
        int month = Int32.Parse(date_components[1]);
        int year = Int32.Parse(date_components[2]);
        return new DateTime(year, month, day);  
    }
    

    public static void Main(String[] args) {


        String jsonfeed_path = args[0];
        String jsonresponse_path = args[1]; 
        
        List<SIInvoice> siinvoices = new();

        // Build batch with common information to all invoices. 
        Party titular = new()
        {
            TaxIdentificationNumber = "B98815608",
            PartyName = "Euromedia Investment Group, S.L."
        };

        var batch = new Batch(BatchActionKeys.LR, BatchActionPrefixes.SuministroLR, BatchTypes.FacturasEmitidas)
        {
            Titular = titular,
            CommunicationType = CommunicationType.A0
        };

        Party emisor = titular;

        // Parsing json file into SIIInvoice and SIILine objects
        using (StreamReader reader  = new StreamReader(jsonfeed_path))
        {
            String json_string = reader.ReadToEnd();
            siinvoices = JsonSerializer.Deserialize<List<SIInvoice>>(json_string);
        }


        if (siinvoices != null)
            if (siinvoices.Count > 0)
            {
                foreach (SIInvoice inv in siinvoices)
                {

                    DateTime issuedate = get_date(inv.invoice_date);
                    ARInvoice arinv = new()
                    {
                        IssueDate = issuedate,
                        OperationIssueDate = issuedate,
                        SellerParty = emisor,
                        InvoiceType = InvoiceType.F1,
                        InvoiceNumber = inv.invoice_number,
                        BuyerParty = new Party()
                        {
                            TaxIdentificationNumber = inv.partner_ident,
                            PartyName = inv.partner_name,
                        },
                        CountryCode = inv.country_code,
                        GrossAmount = Gross_amount(inv)
                    };

                    char type = inv.invoice_number[0];

                    switch (type)
                    {
                        case '1':

                            arinv.InvoiceText = "Operacion Nacional de venta de móviles, accesorios u otros aparatos electrónicos.";
                            arinv.ClaveRegimenEspecialOTrascendencia = ClaveRegimenEspecialOTrascendencia.RegimenComun;

                            Decimal base21 = 0;
                            Decimal base0 = 0;  
                            Decimal tax = 0;
                            
                            foreach (SIILine line in inv.lines)
                                if (line.tax == 0)
                                    base0 += line.price * line.quantity;
                                else if (line.tax == 21)
                                    base21 += line.price * line.quantity;

                            tax = base21 * 21 / 100;

                            
                            if (base0 != 0)
                                arinv.AddTaxOtuput(-(int)CausaExencion.E6, Math.Round(base0, 2), 0);

                            if (base21 != 0)
                                arinv.AddTaxOtuput(21, Math.Round(base21, 2), Math.Round(tax, 2));

                            break;

                        case '2':
                            arinv.InvoiceText = "Operacion Nacional con ISP de venta de móviles,acccesorios u otros aparatos electrónicos.";
                            arinv.ClaveRegimenEspecialOTrascendencia = ClaveRegimenEspecialOTrascendencia.RegimenComun;
                            arinv.ToSII(true);
                            
                            
                            arinv.InnerSII.FacturaExpedida.TipoDesglose.DesgloseFactura.Sujeta.NoExenta = new NoExenta()
                            {
                                TipoNoExenta = inv.ambos_tax ? SujetaType.S3.ToString() : SujetaType.S2.ToString()
                            };

                            arinv.InnerSII.FacturaExpedida.TipoDesglose.DesgloseFactura.Sujeta.NoExenta.DesgloseIVA = new DesgloseIVA(); 

                            base21 = 0; 
                            foreach (SIILine line in inv.lines)
                                if (line.tax == 21)
                                    base21 += line.price * line.quantity;
                            
                            if (base21 != 0)
                                arinv.InnerSII.FacturaExpedida.TipoDesglose.DesgloseFactura.Sujeta.NoExenta.DesgloseIVA.DetalleIVA.Add(new DetalleIVA()
                                    {
                                        BaseImponible = SIIParser.FromDecimal(base21), 
                                        CuotaRepercutida = SIIParser.FromDecimal(base21 * 21 / 100).ToString(), 
                                        TipoImpositivo = "21"

                                    }
                                );

                            Decimal amountisp = 0; 
                            foreach(SIILine line in inv.lines)
                                if (line.is_stock && line.tax == 0)
                                    amountisp += line.price * line.quantity;

                            foreach (SIILine line in inv.lines)
                                if (!line.is_stock && line.tax == 0 && line.price < 0)
                                    amountisp += line.price * line.quantity;


                            arinv.InnerSII.FacturaExpedida.TipoDesglose.DesgloseFactura.Sujeta.NoExenta.DesgloseIVA.DetalleIVA.Add(
                                new DetalleIVA()
                                {
                                    BaseImponible = SIIParser.FromDecimal(amountisp), 
                                    CuotaRepercutida = "0", 
                                    TipoImpositivo = "0"
                                }
                             );

                            Decimal x = 0;
                            foreach (SIILine line in inv.lines)
                                if (!line.is_stock && line.tax == 0 && line.price > 0)
                                    x += line.price * line.quantity;

                            if (x != 0)
                                arinv.InnerSII.FacturaExpedida.TipoDesglose.DesgloseFactura.NoSujeta = new NoSujeta()
                                {
                                    ImportePorArticulos7_14_Otros = SIIParser.FromDecimal(x)
                                };


                            arinv.InnerSII.FacturaExpedida.ImporteTotal = SIIParser.FromDecimal(arinv.GrossAmount);
                            arinv.InnerSII.FacturaExpedida.TipoDesglose.DesgloseFactura.Sujeta.Exenta = null; 
                            break; 
                        
                        case '3':
                            arinv.IDOtroType = IDOtroType.DocOficialPaisResidencia;
                            arinv.InvoiceText = "Exportación: Venta de móviles, accesorios u otros aparatos electrónicos.";
                            arinv.ClaveRegimenEspecialOTrascendencia = ClaveRegimenEspecialOTrascendencia.ExportacionREAGYP;
                            arinv.AddTaxOtuput(-(int)CausaExencion.E2, arinv.GrossAmount, 0);


                            break;
                        case '4':
                            arinv.IDOtroType = IDOtroType.NifIva;
                            arinv.InvoiceText = "Operacion Intracomunitaria de venta de móviles, accesorios u otros aparatos electrónicos.";
                            arinv.ClaveRegimenEspecialOTrascendencia = ClaveRegimenEspecialOTrascendencia.RegimenComun;
                            arinv.AddTaxOtuput(-(int)CausaExencion.E5, arinv.GrossAmount,0);
                            break;


                        case '5':
                            break;
                        case '6':
                            break;
                        default:
                            break;
                    }

                    batch.BatchItems.Add(arinv);
                }


                BatchDispatcher.SendSiiLote(batch);

                List<SIIResponse> responses = new(); 

                foreach (var invoice in batch.BatchItems)
                {
                    SIIResponse sir = new();
                    sir.invoice_date = invoice.GetItemDate().ToString();
                    sir.invoice_number = invoice.GetItemKey().ToString();
                    sir.invoice_status = invoice.Status;
                    sir.message = invoice.ErrorMessage;

                    responses.Add(sir); 

                }

                String json_string = JsonSerializer.Serialize(responses);

                using (StreamWriter writer = new StreamWriter(jsonresponse_path))
                {
                    writer.WriteLine(json_string);
                }

            }
        }
    }

