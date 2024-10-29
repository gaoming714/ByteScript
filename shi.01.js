// 最初要执行这两行
var results = []; // 用于保存每个元素的字典
var repeatCount = 0; // 记录 collectData 执行次数

// 主要有两个函数downloadData collectData
function downloadData() {
    // 将数组转换为JSON字符串
    var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(results));
  
    // 获取当前时间，并格式化为YYYYMMDDHHMMSS
    var now = new Date();
    var fileName = now.toISOString().replace(/[-T:]/g, "").substr(0, 14) + ".json";
  
    // 创建一个下载链接
    var downloadLink = document.createElement("a");
    downloadLink.download = fileName;
    downloadLink.href = dataStr;
    downloadLink.clickvar
  
    // 清除创建的元素
    downloadLink.remove();
}

async function collectData(count) {
    // 获取所有 class=el-table__row 的元素
    const rows = document.querySelectorAll('.el-table__row');
    
    const halfLength = Math.ceil(rows.length / 2);

    // 遍历 rows 的前一半元素
    for (let i = 0; i < halfLength; i++) {
        let row = rows[i];
        let tmp_dict = {}; // 创建临时字典用于存储当前行数据
        
        
        // 获取第一个和第三个 class=el_tooltip 的元素文本
        const markTool = row.querySelectorAll('.el-tooltip')[1];
        const timeTool = row.querySelectorAll('.el-table_1_column_11')[0];
        const nameTool = row.querySelectorAll('.el-tooltip')[12];
        
        if (markTool && timeTool && nameTool) {
            tmp_dict['markTool'] = markTool.textContent.trim();
            tmp_dict['timeTool'] = timeTool.textContent.trim();
            tmp_dict['nameTool'] = nameTool.textContent.trim();
        }

        // 点击 td 中的 class=el-button--text 按钮
        const button = row.querySelector('td .el-button--text');
        if (button) {
            button.click();
            
            // 等待弹出框出现
            await new Promise(resolve => setTimeout(resolve, 500)); // 等待 1 秒

            // 获取弹出框中的 class=el-message-box__message 的值
            const messageBox = document.querySelector('.el-message-box__message');
            if (messageBox) {
                tmp_dict['messageBox'] = messageBox.textContent.trim();
                const match = messageBox.textContent.trim().match(/\d{11}$/);
                if (match) {
                  tmp_dict["msgTool"] = match[0];
                } else {
                  // 如果没有匹配到，则设置默认值或进行其他处理
                  tmp_dict["msgTool"] = "未找到11位数字";
                }
            }

            // 点击关闭按钮
            const closeButton = document.querySelector('.el-message-box__close');
            if (closeButton) {
                closeButton.click();
                await new Promise(resolve => setTimeout(resolve, 300)); // 等待关闭完成
            }
        }

        // 将当前字典保存到结果数组中
        results.push(tmp_dict);

        // 等待 1 秒以便处理下一个元素
        await new Promise(resolve => setTimeout(resolve, 1000));
    }

    console.log("Data collection completed:", results);
        // collectData 执行完毕
    repeatCount++;
    console.log(`CollectData execution count: ${repeatCount}`);
    console.log("Current Data:", results);

    // 检查是否需要继续执行
    if (repeatCount <= count) {
        // 点击 class=el-icon-arrow-right 按钮
        const nextButton = document.querySelector('.btn-next');
        if (nextButton) {
            nextButton.click();
            await new Promise(resolve => setTimeout(resolve, 1000)); // 等待 1 秒
        }

        // 再次调用 collectData 函数
        await collectData(count);
    } else {
        console.log("Data collection completed. Final Results:", results);
    }

}





// 假设有一个数组
//var results = [1, 2, 3, 4, 5];

function downloadData() {
    // 将数组转换为JSON字符串
    var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(results));
  
    // 获取当前时间，并格式化为YYYYMMDDHHMMSS
    var now = new Date();
    var fileName = now.toISOString().replace(/[-T:]/g, "").substr(0, 14) + ".json";
  
    // 创建一个下载链接
    var downloadLink = document.createElement("a");
    downloadLink.download = fileName;
    downloadLink.href = dataStr;
    downloadLink.click();
  
    // 清除创建的元素
    downloadLink.remove();
}



// 启动数据收集
collectData(10);

// 下载
downloadData()