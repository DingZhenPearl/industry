# 数据库列类型迁移说明

本文档提供了将数据库中 `line_id` 和 `machine_id` 列从 INT 类型转换为 VARCHAR 类型的步骤说明。

## 迁移前准备

1. **备份数据库**
   在进行任何迁移操作前，强烈建议先备份您的数据库：
   ```sql
   mysqldump -u root -p industry_db > industry_db_backup.sql
   ```

2. **确认数据库连接信息**
   请确认 `migrate_id_columns.py` 脚本中的数据库连接信息是否正确：
   - 主机名: localhost
   - 用户名: root
   - 密码: 请修改为您的实际密码
   - 数据库名: industry_db

## 执行迁移

1. **运行迁移脚本**
   ```bash
   python pyScripts/migrate_id_columns.py
   ```
   
   此脚本将执行以下操作：
   - 创建临时列并复制现有数据
   - 删除原INT类型列
   - 重命名临时列为正式列
   - 添加列注释

2. **验证迁移结果**
   ```bash
   python pyScripts/verify_migration.py
   ```
   
   此脚本将显示列的数据类型和示例数据，以确认迁移是否成功。

## 迁移后注意事项

1. **前端代码已更新**
   前端代码已经更新，不再对 `line_id` 和 `machine_id` 进行数字转换。

2. **数据库交互**
   所有与数据库交互的Python脚本已更新，以处理字符串格式的ID。

3. **如需回滚**
   如果迁移过程中出现问题，可以使用之前的备份恢复数据库：
   ```sql
   mysql -u root -p industry_db < industry_db_backup.sql
   ```

## 故障排除

如果在迁移过程中遇到问题：

1. 检查数据库连接信息是否正确
2. 确认用户是否有足够的权限执行ALTER TABLE操作
3. 查看MySQL错误日志以获取更详细的错误信息
