struct ocr_result
{
    1: string result;
    2: i32  roi_left;
    3: i32  roi_top;
    4: i32  roi_width;
    5: i32  roi_height;
}

service ocr_server {
    list<ocr_result> scene_ocr(1:list<string> image, 2:bool b_location);
}
