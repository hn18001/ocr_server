namespace cpp CNNPredict

struct Request
{
  1:string inputImage,
  2:i32    imageChannel,
  3:i32    imageWidth ,
  4:i32    imageHeight,
}

struct ROIResult
{
  1:string outputImage,
  2:i32    imageChannel,
  3:i32    imageWidth,
  4:i32    imageHeight  	
}

struct Result
{
  1:ROIResult maskResult, 
  2:list<ROIResult> roiResults
}

service CNNPredictService
{
  list<Result> predict(1:list<Request> s)
}
