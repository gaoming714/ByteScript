package main

import (
        "encoding/json"
        "fmt"
        "os"
        "path/filepath"

        "github.com/360EntSecGroup-Skylar/excelize"
)

func jsonToExcel(jsonFile string) error {
        // 打开JSON文件
        f, err := os.Open(jsonFile)
        if err != nil {
                return err
        }
        defer f.Close()

        // 解析JSON数据
        var data interface{}
        if err := json.NewDecoder(f).Decode(&data); err != nil {
                return err
        }

        // 创建Excel文件
        xlsx := excelize.NewFile()
        index := 1
        sheetName := "Sheet1"

        // 根据JSON数据结构动态设置列名和填充数据
        // 这里假设JSON数据为一个数组，每个元素是一个map
        if jsonData, ok := data.([]interface{}); ok {
                // 获取第一个元素的键作为列名
                keys := make([]string, 0)
                for k := range jsonData[0].(map[string]interface{}) {
                        keys = append(keys, k)
                }

                // 写入列名
                for i, key := range keys {
                        xlsx.SetCellValue(sheetName, fmt.Sprintf("%s%d", string('A'+i), 1), key)
                }

                // 写入数据
                for _, item := range jsonData {
                        for i, key := range keys {
                                xlsx.SetCellValue(sheetName, fmt.Sprintf("%s%d", string('A'+i), index+1), item.(map[string]interface{})[key])
                        }
                        index++
                }
        } else {
                return fmt.Errorf("JSON data format is not supported")
        }

        // 保存Excel文件
        excelFile := filepath.Base(jsonFile) + ".xlsx"
        if err := xlsx.SaveAs(excelFile); err != nil {
                return err
        }
        return nil
}

func main() {
        // 遍历当前目录下的所有文件
        err := filepath.Walk(".", func(path string, info os.FileInfo, err error) error {
                if err != nil {
                        return err
                }
                if !info.IsDir() && filepath.Ext(path) == ".json" {
                        if err := jsonToExcel(path); err != nil {
                                fmt.Printf("Error converting %s: %s\n", path, err)
                        } else {
                                fmt.Printf("Converted %s to Excel successfully\n", path)
                        }
                }
                return nil
        })
        if err != nil {
                fmt.Println(err)
        }
}
