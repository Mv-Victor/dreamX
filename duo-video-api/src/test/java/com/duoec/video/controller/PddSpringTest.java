package com.duoec.video.controller;

import com.duoec.base.core.util.JsonUtils;
import com.duoec.base.dto.response.BaseResponse;
import com.duoec.video.dto.request.*;
import com.duoec.video.jy.JianyingBuilder;
import com.duoec.video.jy.JianyingProjectBuildState;
import com.duoec.video.jy.service.impl.StorageServiceImpl;
import com.duoec.video.project.VideoProject;
import com.duoec.video.project.material.TextStyle;
import com.fasterxml.jackson.core.type.TypeReference;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(classes = com.duoec.video.TestConfiguration.class)
@AutoConfigureMockMvc
class PddSpringTest {
    static {
        JianyingBuilder.storageService = new StorageServiceImpl();
        JianyingProjectBuildState.DEBUG_JY_DRAFT_DIR = "/root/dreamX/tmp/jy-drafts/";
    }

    @Autowired
    private MockMvc mockMvc;

    private static final long PROJECT_ID = 200003L;
    private static final String BASE_PATH = "file:///root/dreamX/doc/sale/pdd_spring/";

    private static final long[][] TIMING = {
            {0, 2900},
            {2900, 2800},
            {5700, 3200},
            {8900, 2900},
    };

    private static final String[] SUBTITLES = {
            "拼多多春节不放假？！",
            "员工竟然说不想双休",
            "这加班文化太离谱了",
            "你能接受这种工作吗",
    };

    private static final long TOTAL_DURATION = 11800L;

    @Test
    void testBuildPddSpring() throws Exception {
        // 1. 创建项目
        CreateProjectRequest createReq = new CreateProjectRequest();
        createReq.setProjectId(PROJECT_ID);
        createReq.setProjectName("PDD春节加班_小红书营销");
        createReq.setWidth(1080);
        createReq.setHeight(1920);

        MvcResult createResult = mockMvc.perform(post("/api/project")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(JsonUtils.toJsonString(createReq)))
                .andExpect(status().isOk())
                .andReturn();
        BaseResponse<VideoProject> createResp = JsonUtils.toObject(createResult.getResponse().getContentAsString(), new TypeReference<>() {});
        assertEquals(0, createResp.getCode());
        System.out.println("1. 创建项目成功");

        // 2-5. 添加4张图片
        for (int i = 0; i < 4; i++) {
            addImage(PROJECT_ID, 200301L + i, BASE_PATH + (i + 1) + ".jpg",
                    TIMING[i][0], TIMING[i][1],
                    (i + 2) + ". 添加图片" + (i + 1) + "成功");
        }

        // 6. 添加背景音乐
        AddAudioRequest bgm = new AddAudioRequest();
        bgm.setProjectId(PROJECT_ID);
        bgm.setScriptIndex(0);
        bgm.setAudioId(200400L);
        bgm.setAudioUrl(BASE_PATH + "bgm.mp3");
        bgm.setStartTime(0L);
        bgm.setDuration(TOTAL_DURATION);
        bgm.setMaterialTimeStart(0L);
        bgm.setMaterialTimeEnd(127500L);
        bgm.setVolume(-30);
        callApi("/api/project/audio", bgm, "6. 添加背景音乐成功");

        // 7-10. 添加4条配音
        for (int i = 0; i < 4; i++) {
            AddAudioRequest vo = new AddAudioRequest();
            vo.setProjectId(PROJECT_ID);
            vo.setScriptIndex(0);
            vo.setAudioId(200401L + i);
            vo.setAudioUrl(BASE_PATH + "voiceover_" + (i + 1) + ".mp3");
            vo.setStartTime(TIMING[i][0]);
            vo.setDuration(TIMING[i][1]);
            vo.setVolume(0);
            callApi("/api/project/audio", vo, (i + 7) + ". 添加配音" + (i + 1) + "成功");
        }

        // 11-14. 添加4条字幕
        for (int i = 0; i < 4; i++) {
            String fillColor = (i == 3) ? "#FFD700" : "#FFFFFF";
            addSubtitle(PROJECT_ID, SUBTITLES[i], TIMING[i][0], TIMING[i][1], fillColor,
                    (i + 11) + ". 添加字幕" + (i + 1) + "成功");
        }

        // 15. 构建工程
        BuildProjectRequest buildReq = new BuildProjectRequest();
        buildReq.setProjectId(PROJECT_ID);
        buildReq.setVideoId(PROJECT_ID);

        MvcResult buildResult = mockMvc.perform(post("/api/project/build")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(JsonUtils.toJsonString(buildReq)))
                .andExpect(status().isOk())
                .andReturn();
        BaseResponse<Long> buildResp = JsonUtils.toObject(buildResult.getResponse().getContentAsString(), new TypeReference<>() {});
        assertEquals(0, buildResp.getCode());
        assertNotNull(buildResp.getData());
        System.out.println("15. 构建成功, taskId: " + buildResp.getData());

        // 16. 读取任务文件获取 COS URL
        long taskId = buildResp.getData();
        java.io.File taskFile = new java.io.File("tmp/task_0/" + taskId + ".json");
        if (taskFile.exists()) {
            String taskJson = new String(java.nio.file.Files.readAllBytes(taskFile.toPath()));
            System.out.println("=== 任务详情 ===");
            System.out.println(taskJson);
        }
    }

    private void addImage(long projectId, long imageId, String imageUrl, long startTime, long duration, String msg) throws Exception {
        AddImageRequest img = new AddImageRequest();
        img.setProjectId(projectId);
        img.setScriptIndex(0);
        img.setImageId(imageId);
        img.setImageUrl(imageUrl);
        img.setStartTime(startTime);
        img.setDuration(duration);
        img.setZoomX(10000);
        img.setZoomY(10000);
        img.setPositionX(0);
        img.setPositionY(0);
        callApi("/api/project/image", img, msg);
    }

    private void addSubtitle(long projectId, String text, long startTime, long duration, String fillColor, String msg) throws Exception {
        AddTextRequest textReq = new AddTextRequest();
        textReq.setProjectId(projectId);
        textReq.setScriptIndex(0);
        textReq.setText(text);
        textReq.setStartTime(startTime);
        textReq.setDuration(duration);
        textReq.setPositionX(0);
        textReq.setPositionY(-750);
        textReq.setAsSubtitle(true);
        textReq.setStyle(new TextStyle()
                .setFontSize(8)
                .setBold(true)
                .setTextAlign(1)
                .setFontName("抖音美好体")
                .setFillColor(fillColor)
                .setStrokeColor("#000000")
                .setStrokeWidth(10));
        callApi("/api/project/text", textReq, msg);
    }

    private void callApi(String path, Object request, String msg) throws Exception {
        MvcResult result = mockMvc.perform(post(path)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(JsonUtils.toJsonString(request)))
                .andExpect(status().isOk())
                .andReturn();
        BaseResponse<?> resp = JsonUtils.toObject(result.getResponse().getContentAsString(), new TypeReference<BaseResponse<Object>>() {});
        assertEquals(0, resp.getCode(), "Failed: " + msg);
        System.out.println(msg);
    }
}
