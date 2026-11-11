param (
    [string]$DocxPath = "$PSScriptRoot\..\informe\Informe_Examen2M_Ronald_Saavedra.docx",
    [string]$PdfPath = "$PSScriptRoot\..\informe\Informe_Examen2M_Ronald_Saavedra.pdf"
)

$resolvedDocx = (Resolve-Path $DocxPath).Path
$resolvedPdf = [System.IO.Path]::GetFullPath($PdfPath)

Write-Host "[*] Exportando $resolvedDocx a PDF..."
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($resolvedDocx)
    $wdFormatPDF = 17
    $doc.SaveAs([ref]$resolvedPdf, [ref]$wdFormatPDF)
    $doc.Close()
    Write-Host "[+] PDF generado con exito: $resolvedPdf"
}
finally {
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
