


$adobe='C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe'
$printername='\\EUROMEDIA-WH1\DHL in Warehouse'
$drivername='ZDesigner ZD420-203dpi ZPL'
$portname='USB002'
$pdf='.\dhl 4-000495.pdf'
$arglist='/S /T "{0}" "{1}" "{2}" {3}' -f $pdf, $printername, $drivername, $portname

Start-Process $adobe -ArgumentList $arglist

