while true
do
	python run_console.py report_parser;
	sleep 5;
	python run_console.py payment_info;
	sleep 5;
	python run_console.py payment_auto;
	sleep 10;
done
