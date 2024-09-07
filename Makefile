all:
	@echo "Not Done!"
	pm2 status
atom:
	pm2 start ./daemon/atom.sh --name atom --silent --log --cron-restart="1 0 * * *"

router:
	pm2 start ./daemon/ranger_fox.sh --name ranger_fox --silent --log
	pm2 start ./daemon/ranger_claw.sh --name ranger_claw --silent --log

algo:
	pm2 start ./daemon/algo_chat.sh --name algo_chat --silent --log
	pm2 start ./daemon/algo_turn.sh --name algo_turn --silent --log

tool:
	pm2 start ./daemon/runtime_email.sh --name run_email --silent --log
	pm2 start ./daemon/runtime_wechat.sh --name run_wechat --silent --log

live:
	pm2 start ./daemon/live_main.sh --name live_main --silent --log

daren:
	pm2 start ./daemon/daren.sh --name daren.puppy0 --silent --log
	pm2 start ./daemon/daren.sh --name daren.puppy1 --silent --log

rebuild:
	pm2 start ./daemon/rebuild.22.sh --name rebuild.22 --silent --log
	pm2 start ./daemon/rebuild.23.sh --name rebuild.23 --silent --log

status:
	pm2 status

clean:
	pm2 delete daren.puppy0
	pm2 delete daren.puppy1
	pm2 delete daren.puppy2
	pm2 delete daren.puppy3
	pm2 delete daren.puppy4
	pm2 delete daren.puppy5
