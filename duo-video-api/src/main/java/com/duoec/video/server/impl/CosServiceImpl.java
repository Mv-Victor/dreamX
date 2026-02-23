package com.duoec.video.server.impl;

import com.duoec.video.config.CosConfig;
import com.duoec.video.server.CosService;
import com.qcloud.cos.COSClient;
import com.qcloud.cos.model.PutObjectRequest;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.autoconfigure.condition.ConditionalOnBean;
import org.springframework.stereotype.Service;

import java.io.File;
import java.net.URL;
import java.util.Date;

@Service
@RequiredArgsConstructor
@ConditionalOnBean(COSClient.class)
public class CosServiceImpl implements CosService {
    private static final Logger logger = LoggerFactory.getLogger(CosServiceImpl.class);

    private final COSClient cosClient;
    private final CosConfig cosConfig;

    @Override
    public String upload(File file, String cosKey) {
        String fullKey = cosConfig.getKeyPrefix() + cosKey;
        logger.info("上传文件到 COS: {} -> {}", file.getAbsolutePath(), fullKey);

        PutObjectRequest putRequest = new PutObjectRequest(cosConfig.getBucket(), fullKey, file);
        cosClient.putObject(putRequest);

        // 直接拼接公有读 URL（无签名，永久有效）
        String url = String.format("https://%s.cos.%s.myqcloud.com/%s",
                cosConfig.getBucket(), cosConfig.getRegion(), fullKey);

        logger.info("COS 上传完成, 下载链接: {}", url);
        return url;
    }
}
