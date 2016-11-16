1. 使用本服务之前，需要在ocr_project_path中编译libcrnn.so;
2. Torch默认会使用所有的GPU设备，如果只需要使用其中的一块卡，可以这样设置：
    1）export CUDA_VISIBLE_DEVICES=1    #只使用第2个卡，卡号从0开始
    2）python ./server.py
