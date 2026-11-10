<#
.SYNOPSIS
  Instala a rule de comentarios no projeto atual. Windows PowerShell 5.1 e PowerShell 7 (Windows, macOS, Linux).
.EXAMPLE
  irm https://raw.githubusercontent.com/lluiseduardo-silva/agents-comments-rule/main/install.ps1 | iex
.EXAMPLE
  & ([scriptblock]::Create((irm https://raw.githubusercontent.com/lluiseduardo-silva/agents-comments-rule/main/install.ps1))) -Harness agents
.EXAMPLE
  .\install.ps1 -Harness cursor -Target C:\code\meu-projeto
.EXAMPLE
  .\install.ps1 -Uninstall
.PARAMETER Harness
  Onde gravar a rule. claude: .claude/rules/comments.md (padrao). agents: bloco gerenciado em AGENTS.md.
  gemini: bloco em GEMINI.md. copilot: bloco em .github/copilot-instructions.md.
  cursor: .cursor/rules/comments.mdc (alwaysApply).
.PARAMETER Target
  Raiz do projeto. Padrao: diretorio atual.
.PARAMETER Dest
  Grava a rule inteira nesse arquivo, para qualquer harness.
.PARAMETER Block
  Grava a rule como bloco gerenciado dentro desse arquivo.
.PARAMETER Global
  Com -Harness claude: instala em ~/.claude/rules (todos os projetos).
.PARAMETER Ref
  Branch ou tag de onde baixar. Padrao: main.
.PARAMETER Force
  Sobrescreve um arquivo que nao parece ser desta rule.
.PARAMETER Uninstall
  Remove o que este script instalou.
#>
param(
  [ValidateSet('claude', 'agents', 'gemini', 'copilot', 'cursor')][string]$Harness = 'claude',
  [string]$Target = '.',
  [string]$Dest = '',
  [string]$Block = '',
  [string]$Ref = 'main',
  [switch]$Global,
  [switch]$Force,
  [switch]$Uninstall
)

# Tudo roda em um escopo filho: sob "irm | iex" o script e avaliado na sessao de quem chamou,
# e assim nao altera $ErrorActionPreference dela nem a encerra em caso de erro.
& {
  param($Harness, $Target, $Dest, $Block, $Ref, $Global, $Force, $Uninstall, $ScriptRoot)
  $ErrorActionPreference = 'Stop'
  $repo = 'lluiseduardo-silva/agents-comments-rule'
  $start = '<!-- agents-comments-rule:start'
  $end = '<!-- agents-comments-rule:end'
  $utf8 = New-Object System.Text.UTF8Encoding($false)

  if (-not (Test-Path -LiteralPath $Target -PathType Container)) { throw "diretorio nao encontrado: $Target" }
  $targetFull = (Resolve-Path -LiteralPath $Target).Path

  # mode=file grava um arquivo so da rule; mode=block mantem um bloco dentro de um arquivo compartilhado.
  $mode = 'file'
  $front = ''
  if ($Dest) { $path = $Dest }
  elseif ($Block) { $path = $Block; $mode = 'block' }
  else {
    switch ($Harness) {
      'claude' {
        if ($Global) { $path = Join-Path (Join-Path (Join-Path $HOME '.claude') 'rules') 'comments.md' }
        else { $path = '.claude/rules/comments.md' }
      }
      'agents' { $path = 'AGENTS.md'; $mode = 'block' }
      'gemini' { $path = 'GEMINI.md'; $mode = 'block' }
      'copilot' { $path = '.github/copilot-instructions.md'; $mode = 'block' }
      'cursor' { $path = '.cursor/rules/comments.mdc'; $front = 'cursor' }
    }
  }
  if ([System.IO.Path]::IsPathRooted($path)) { $full = $path } else { $full = Join-Path $targetFull $path }
  $full = [System.IO.Path]::GetFullPath($full)

  function Read-Text($p) { [System.IO.File]::ReadAllText($p, [System.Text.Encoding]::UTF8) }
  function Test-Ours($text) { $text -match '(?m)^# Code comments' }
  # Devolve o texto sem o bloco gerenciado e sem linhas em branco no fim.
  function Remove-Block($text) {
    $pattern = '(?ms)^' + [regex]::Escape($start) + '.*?^' + [regex]::Escape($end) + '[^\n]*\n?'
    ([regex]::Replace($text, $pattern, '')).TrimEnd()
  }

  if ($Uninstall) {
    if (-not (Test-Path -LiteralPath $full -PathType Leaf)) { Write-Host "nada instalado em $full"; return }
    $current = Read-Text $full
    if ($mode -eq 'block') {
      $rest = Remove-Block $current
      if ($rest) { [System.IO.File]::WriteAllText($full, $rest + "`n", $utf8); Write-Host "bloco removido de $full" }
      else { Remove-Item -LiteralPath $full -Force; Write-Host "removido  $full" }
    }
    elseif ((Test-Ours $current) -or $Force) {
      Remove-Item -LiteralPath $full -Force
      Write-Host "removido  $full"
      # Remove as pastas que ficaram vazias, ate dois niveis acima do arquivo.
      $dir = Split-Path -Parent $full
      foreach ($level in 1..2) {
        if ((Get-ChildItem -LiteralPath $dir -Force) -or ($dir -eq $targetFull)) { break }
        Remove-Item -LiteralPath $dir -Force
        $dir = Split-Path -Parent $dir
      }
    }
    else { throw "$full nao parece ser esta rule; use -Force para remover mesmo assim." }
    return
  }

  # Fonte: o arquivo ao lado deste script quando roda de um clone; senao, download.
  $local = ''
  if ($ScriptRoot) { $local = Join-Path (Join-Path $ScriptRoot 'rule') 'comments.md' }
  if ($local -and (Test-Path -LiteralPath $local -PathType Leaf)) {
    $rule = Read-Text $local
  }
  else {
    $url = "https://raw.githubusercontent.com/$repo/$Ref/rule/comments.md"
    try { [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12 } catch {}
    $client = New-Object System.Net.WebClient
    try { $rule = [System.Text.Encoding]::UTF8.GetString($client.DownloadData($url)) }
    finally { $client.Dispose() }
  }
  if (-not (Test-Ours $rule)) { throw "o conteudo obtido nao e a rule esperada (ref: $Ref)" }
  $rule = $rule.Replace("`r`n", "`n")
  if (-not $rule.EndsWith("`n")) { $rule += "`n" }

  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $full) | Out-Null
  if ($mode -eq 'block') {
    $rest = ''
    if (Test-Path -LiteralPath $full -PathType Leaf) { $rest = Remove-Block (Read-Text $full) }
    $text = ''
    if ($rest) { $text = $rest + "`n`n" }
    $text += "$start (gerenciado por install.ps1; edite fora deste bloco) -->`n" + $rule + "$end -->`n"
    [System.IO.File]::WriteAllText($full, $text, $utf8)
    Write-Host "instalado bloco em $full"
  }
  else {
    if ((Test-Path -LiteralPath $full -PathType Leaf) -and -not (Test-Ours (Read-Text $full)) -and -not $Force) {
      throw "$full ja existe e nao parece ser esta rule. Use -Block para acrescentar a ele, ou -Force para sobrescrever."
    }
    $text = $rule
    if ($front -eq 'cursor') {
      $text = "---`ndescription: Code comment standard - contract docs, mutation stated, no narrative`nalwaysApply: true`n---`n`n" + $rule
    }
    [System.IO.File]::WriteAllText($full, $text, $utf8)
    Write-Host "instalado $full"
  }
} $Harness $Target $Dest $Block $Ref $Global.IsPresent $Force.IsPresent $Uninstall.IsPresent $PSScriptRoot
