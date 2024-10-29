package main

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/xuri/excelize/v2"
)

func main() {
	// 存储 msgTool 的 map 用于去重
	msgMap := make(map[string]bool)

	// 创建新的 Excel 文件用于合并
	mergedFile := excelize.NewFile()
	mergedSheet := "Sheet1"
	mergedFile.NewSheet(mergedSheet)

	// 行计数器，起始行为 1（标题行）
	rowCounter := 1

	// 获取当前目录下的所有 Excel 文件
	err := filepath.Walk(".", func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		// 仅处理 .xlsx 文件
		if !info.IsDir() && filepath.Ext(path) == ".xlsx" {
			fmt.Println("正在处理文件:", path)

			// 打开 Excel 文件
			f, err := excelize.OpenFile(path)
			if err != nil {
				return err
			}

			// 获取第一个 Sheet
			sheetName := f.GetSheetName(0)

			// 读取文件内容
			rows, err := f.GetRows(sheetName)
			if err != nil {
				return err
			}

			// 如果是第一次读取，写入标题行
			if rowCounter == 1 && len(rows) > 0 {
				for colID, cellValue := range rows[0] {
					colName, _ := excelize.ColumnNumberToName(colID + 1)
					mergedFile.SetCellValue(mergedSheet, fmt.Sprintf("%s%d", colName, rowCounter), cellValue)
				}
				rowCounter++
			}

			// 查找 msgTool 列索引
			msgToolColIdx := -1
			if len(rows) > 0 {
				for i, col := range rows[0] {
					if col == "msgTool" {
						msgToolColIdx = i
						break
					}
				}
			}

			// 处理数据行
			for _, row := range rows[1:] {
				// 检查 msgTool 列是否存在
				if msgToolColIdx != -1 && len(row) > msgToolColIdx {
					msgValue := row[msgToolColIdx] // 获取 msgTool 列的值
					if !msgMap[msgValue] {
						// 如果 msg 值不重复，添加到合并文件并标记
						for colID, cellValue := range row {
							colName, _ := excelize.ColumnNumberToName(colID + 1)
							mergedFile.SetCellValue(mergedSheet, fmt.Sprintf("%s%d", colName, rowCounter), cellValue)
						}
						rowCounter++
						msgMap[msgValue] = true
					}
				}
			}
			f.Close()
		}
		return nil
	})

	if err != nil {
		fmt.Println("文件处理失败:", err)
		return
	}

	// 保存合并后的文件
	err = mergedFile.SaveAs("merged.xlsx")
	if err != nil {
		fmt.Println("合并文件保存失败:", err)
		return
	}

	fmt.Println("合并完成，文件保存为 merged.xlsx")
}
