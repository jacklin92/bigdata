# Docker Compose 是甚麼?

Docker Compose 是一個用於定義和執行多容器 Docker 應用程式的工具。

它使用一個 YAML 檔案 (docker-compose.yml) 來設定應用程式所需的所有服務 (例如網頁伺服器、資料庫、快取等)、網路和儲存卷 (volumes)。

透過單一指令 (docker-compose up 或 docker-compose down)，您就可以建立、啟動、停止和管理整個應用程式堆疊，簡化了開發、測試和部署流程。

# 常用的 Docker Compose 命令

* **啟動服務:**
  * `docker-compose up`: 在前景建立並啟動所有服務的容器。如果容器已存在但設定有變更，會重新建立。您會看到所有容器的日誌輸出。按 `Ctrl+C` 停止。
  * `docker-compose up -d`: 在背景 (detached mode) 建立並啟動所有服務的容器。
  * `docker-compose up --build`: 在啟動前強制重新建置映像檔。
  * `docker-compose up <service_name>`: 只啟動指定的服務及其依賴項。

* **停止與移除服務:**
  * `docker-compose down`: 停止並移除由 `up` 指令建立的容器、網路。預設不會移除 volume。
  * `docker-compose down -v`: 停止並移除容器、網路以及**命名 volume** (named volumes)。
  * `docker-compose stop`: 停止正在執行的容器，但不移除它們。
  * `docker-compose rm`: 移除已停止的服務容器。

* **管理容器與映像檔:**
  * `docker-compose build`: 建置或重新建置服務的映像檔。
  * `docker-compose build <service_name>`: 只建置指定服務的映像檔。
  * `docker-compose pull`: 拉取服務所需的映像檔。
  * `docker-compose push`: 推送服務的映像檔到倉庫 (如果已設定)。

* **查看狀態與日誌:**
  * `docker-compose ps`: 列出 Compose 專案中的容器狀態。
  * `docker-compose logs`: 顯示所有服務容器的日誌。
  * `docker-compose logs -f`: 持續追蹤 (follow) 顯示日誌輸出。
  * `docker-compose logs <service_name>`: 只顯示指定服務的日誌。
  * `docker-compose top`: 顯示各個服務容器內執行的程序。

* **執行命令:**
  * `docker-compose exec <service_name> <command>`: 在一個**正在執行**的容器內執行命令。例如：`docker-compose exec web python manage.py migrate`。
  * `docker-compose run <service_name> <command>`: 為服務**建立一個新容器**並執行一次性命令。例如：`docker-compose run web python manage.py shell` (會啟動一個新的 `web` 容器來執行 shell)。

* **其他:**
  * `docker-compose config`: 驗證並顯示最終合併後的 Compose 設定檔。
  * `docker-compose restart`: 重新啟動所有服務的容器。
  * `docker-compose restart <service_name>`: 重新啟動指定服務的容器。

這些命令通常需要在包含 docker-compose.yml 檔案的目錄下執行。
