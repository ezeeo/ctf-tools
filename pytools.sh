#!/bin/sh
result1=`python ./Library/utils/output_pyver.py`
result2=`python3 ./Library/utils/output_pyver.py`

python_path="python3"
if [ ${#python_path} -eq 0 ]
then
    run_mode="0"
else
    run_mode="1"
fi

if [ $result1 -eq "3" ]
then
    python_path="python"
elif [ $result2 -eq "3" ]
then
    if [ $run_mode -eq "0" ]
    then
        run_mode="2"
    fi
    python_path="python3"
else
    run_mode="2"
    python_path=userinput
fi

if [ $run_mode -eq "0" ]
then
    $python_path tool_manager.py
elif [ $run_mode -eq "1" ]
then
    $python_path tool_manager.py \#
elif [ $run_mode -eq "2" ]
then
    $python_path tool_manager.py $python_path
else
    echo "unknow run mode"
fi
exit

userinput(){
    echo "python environment error"
    read -p "input python path and start:" path
    return $path
}