package com.duoec.video.dto.request;

import lombok.Data;

import java.io.Serializable;

/**
 * 构建视频工程请求
 */
@Data
public class BuildProjectRequest implements Serializable {
    /**
     * 视频工程ID
     */
    private Long projectId;

    /**
     * 视频ID（用于创建任务）
     */
    private Long videoId;

    /**
     * 任务优先级，越小越优先，默认1000
     */
    private Integer priority;
}
