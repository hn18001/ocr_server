function recognize(img_path)
    print("img_path: "..img_path)
    t0 = os.clock()

    local resstr = ""
    local img = loadAndResizeImage(img_path)
    if img == nil then
        print('invalid: ', image_path)
    else
        local text, raw = recognizeImageLexiconFree(model, img)

        ch_tb = split(text, ' ')

        for k = 1, #ch_tb do
            cid = tonumber(ch_tb[k])
            if cid ~= nil then
                --print(cid)
                local char = id2char_tb[cid-1] --first cid is space
                --print(char)
                resstr = resstr..char
            end
        end
    end
    print(resstr)
    print(string.format('ocr\'s time : %.2fs', os.clock() - t0))
        
    return resstr
end
