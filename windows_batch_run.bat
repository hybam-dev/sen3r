@echo off
call C:/ProgramData/Anaconda3/Scripts/activate.bat sen3r

python -V

for /r %%i in (*.geojson) do (
	:: python D:\git-repos\sen3r\batch_sen3r.py -v
	python D:\git-repos\sen3r\batch_sen3r.py "D:\S3\WFR_sample" "D:\S3\s3_batch_test" %%i
)

pause