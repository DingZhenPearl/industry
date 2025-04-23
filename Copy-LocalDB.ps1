# PowerShell 脚本用于将本地数据库复制到 Docker 容器

# 配置变量
$LocalMySqlUser = "root"
$LocalMySqlPassword = "mwYgR7#*X2"  # 替换为您本地 MySQL 的密码
$DockerMySqlUser = "root"
$DockerMySqlPassword = "mwYgR7#*X2"
$DbName = "industry_db"
$BackupFile = "industry_db_backup.sql"
$ContainerName = "industry-mysql"

# 检查 Docker 是否安装
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker 未安装，请先安装 Docker"
    exit 1
}

# 检查 MySQL 容器是否运行
$containerRunning = docker ps | Select-String -Pattern $ContainerName
if (-not $containerRunning) {
    Write-Error "MySQL 容器未运行，请先启动容器。运行: docker-compose up -d mysql"
    exit 1
}

Write-Host "开始从本地数据库导出数据..." -ForegroundColor Green

# 尝试找到 mysqldump 命令
$mysqldumpPaths = @(
    "mysqldump",
    "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe",
    "C:\Program Files\MySQL\MySQL Server 5.7\bin\mysqldump.exe"
)

$mysqldumpCmd = $null
foreach ($path in $mysqldumpPaths) {
    try {
        if ($path -eq "mysqldump") {
            if (Get-Command $path -ErrorAction SilentlyContinue) {
                $mysqldumpCmd = $path
                break
            }
        } elseif (Test-Path $path) {
            $mysqldumpCmd = $path
            break
        }
    } catch {
        # 继续尝试下一个路径
    }
}

if (-not $mysqldumpCmd) {
    Write-Error "找不到 mysqldump 命令，请手动导出数据库"
    exit 1
}

# 导出本地数据库
try {
    Write-Host "使用 $mysqldumpCmd 导出数据库..."
    & $mysqldumpCmd -u $LocalMySqlUser -p"$LocalMySqlPassword" --databases $DbName > $BackupFile
} catch {
    Write-Error "数据库导出失败: $_"
    exit 1
}

if (-not (Test-Path $BackupFile)) {
    Write-Error "数据库导出失败，未生成备份文件"
    exit 1
}

$fileSize = (Get-Item $BackupFile).Length
Write-Host "数据库导出成功，文件大小: $fileSize 字节" -ForegroundColor Green
Write-Host "将备份文件复制到 Docker 容器..." -ForegroundColor Green

# 复制 SQL 文件到容器
docker cp $BackupFile "${ContainerName}:/tmp/"

Write-Host "在 Docker 容器中导入数据..." -ForegroundColor Green

# 在容器中执行 SQL 文件
Get-Content $BackupFile | docker exec -i $ContainerName mysql -u$DockerMySqlUser -p"$DockerMySqlPassword"

# 检查导入结果
Write-Host "验证数据导入..." -ForegroundColor Green
docker exec -i $ContainerName mysql -u$DockerMySqlUser -p"$DockerMySqlPassword" -e "USE $DbName; SHOW TABLES;"

Write-Host "数据库复制完成！" -ForegroundColor Green
Write-Host "重启应用容器以应用更改: docker-compose restart app" -ForegroundColor Yellow
