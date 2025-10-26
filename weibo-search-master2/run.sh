#!/bin/bash

start_date="2009-01-01"
end_date="2024-08-25"

# 检查是否提供了两个参数
if [ "$#" -ne 2 ]; then
    echo "Usage: sh run.sh <start_index> <end_index>"
    exit 1
fi

# 读取命令行参数
start_index=$1
end_index=$2

# 定义文件路径
csv_file="tags.csv"
settings_file="weibo/settings.py"

# 检查 settings.py 文件是否存在
if [ ! -f "$settings_file" ]; then
    echo "Error: settings.py file does not exist."
    exit 1
fi

# 检查 CSV 文件是否存在
if [ ! -f "$csv_file" ]; then
    echo "Error: CSV file does not exist."
    exit 1
fi

# 读取 CSV 文件中指定索引的标签
tags=()
echo "Processing CSV file, please wait..."
while IFS=, read -r tag
do
    index=$(echo "$tag" | cut -d ',' -f 1) # 索引在第一列
    if [ "$index" -ge "$start_index" ] && [ "$index" -le "$end_index" ]; then
        tags+=("$tag")
    fi
done < "$csv_file"

# 替换变量的值
for tag in "${tags[@]}"; do
    # CSV 文件的第二列是标签
    TAG_NAME=$(echo "$tag" | cut -d ',' -f 2)
    echo "================================================================================================================"
    echo "Processing tag: $TAG_NAME"
    sed -i '' "s/^START_DATE = '.*/START_DATE = '$start_date'/g" weibo/settings.py
    sed -i '' "s/^END_DATE = '.*/END_DATE = '$end_date'/g" weibo/settings.py
    sed -i '' "s/^KEYWORD_LIST = .*/KEYWORD_LIST = ['$TAG_NAME']/g" weibo/settings.py
    scrapy crawl search -s JOBDIR=crawls/search
done

