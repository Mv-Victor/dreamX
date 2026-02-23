package com.duoec.video.server;

import java.io.File;

/**
 * COS 上传服务
 */
public interface CosService {
    /**
     * 上传文件到 COS
     * @param file 本地文件
     * @param cosKey COS 对象键
     * @return 预签名下载链接
     */
    String upload(File file, String cosKey);
}
