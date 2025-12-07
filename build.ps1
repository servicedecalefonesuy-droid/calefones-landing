$RootPath = "$HOME\Desktop\calefones-landing"
# Cargar lista simple de marcas (para compatibilidad)
$brandsList = Get-Content -Raw -Path "$RootPath\data\brands.json" | ConvertFrom-Json
# Cargar catálogo detallado
$catalog = Get-Content -Raw -Path "$RootPath\data\catalog.json" | ConvertFrom-Json

# Obtener templates
$templates = Get-ChildItem -Path "$RootPath\templates" -Recurse -Filter "*.html"
$modelTplContent = Get-Content -Raw -Path "$RootPath\templates\modelo.html"

foreach($bName in $brandsList){
    $slug = ($bName -replace '\s+','-').ToLower()
    $brandBaseDir = "$RootPath\public\$slug"
    
    Write-Host "Procesando marca: $bName"

    # Buscar datos detallados en el catálogo
    $brandData = $catalog | Where-Object { $_.brand -eq $bName }
    
    # Generar HTML de lista de modelos para inyectar en index.html
    $modelListHtml = ""
    if ($brandData) {
        $modelListHtml = "<ul class='model-list'>"
        foreach ($m in $brandData.models) {
            $modelListHtml += "<li><a href='./modelos/$($m.id).html'><strong>$($m.name)</strong></a>: $($m.description)</li>"
        }
        $modelListHtml += "</ul>"
    } else {
        $modelListHtml = "<p>Selecciona la guía general a continuación.</p>"
    }

    # Procesar templates estándar
    foreach($tpl in $templates){
        # Ignorar el template base de modelo, ese se procesa aparte
        if ($tpl.Name -eq "modelo.html") { continue }

        $relativePath = $tpl.FullName.Substring(($RootPath + "\templates").Length + 1)
        $destPath = Join-Path -Path $brandBaseDir -ChildPath $relativePath
        $destDir = Split-Path -Path $destPath -Parent

        if (!(Test-Path -Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }

        $content = Get-Content -Raw -Path $tpl.FullName
        $contentOut = $content -replace '{{brand}}', $bName
        $contentOut = $contentOut -replace '{{modelListHtml}}', $modelListHtml

        Set-Content -Path $destPath -Value $contentOut -Encoding UTF8
    }

    # Generar páginas específicas de modelos si existen datos
    if ($brandData) {
        $modelsDir = "$brandBaseDir\modelos"
        if (!(Test-Path -Path $modelsDir)) { New-Item -ItemType Directory -Path $modelsDir -Force | Out-Null }

        foreach ($m in $brandData.models) {
            $mContent = $modelTplContent -replace '{{brand}}', $bName
            $mContent = $mContent -replace '{{modelName}}', $m.name
            $mContent = $mContent -replace '{{modelDesc}}', $m.description
            $mContent = $mContent -replace '{{specResistencia}}', $m.specs.resistencia
            $mContent = $mContent -replace '{{specTermostato}}', $m.specs.termostato
            $mContent = $mContent -replace '{{specAnodo}}', $m.specs.anodo
            $mContent = $mContent -replace '{{specHerramientas}}', ($m.specs.herramientas -join ", ")
            
            Set-Content -Path "$modelsDir\$($m.id).html" -Value $mContent -Encoding UTF8
        }
    }
}
Write-Host "Generación completada."
