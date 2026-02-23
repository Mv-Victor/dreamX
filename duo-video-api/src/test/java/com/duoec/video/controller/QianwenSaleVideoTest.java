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
class QianwenSaleVideoTest {
    static {
        JianyingBuilder.storageService = new StorageServiceImpl();
        JianyingProjectBuildState.DEBUG_JY_DRAFT_DIR = "/root/dreamX/tmp/jy-drafts/";
    }

    @Autowired
    private MockMvc mockMvc;

    @Test
    void testBuildQianwenSaleVideo() throws Exception {
        long projectId = 100001L;

        // 1. 创建项目
        CreateProjectRequest createReq = new CreateProjectRequest();
        createReq.setProjectId(projectId);
        createReq.setProjectName("千问奶茶事件_脉脉营销");
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

        // 2. 添加图片1 (0-6s)
        AddImageRequest img1 = new AddImageRequest();
        img1.setProjectId(projectId);
        img1.setScriptIndex(0);
        img1.setImageId(100101L);
        img1.setImageUrl("file:///root/dreamX/doc/sale/1.png");
        img1.setStartTime(0L);
        img1.setDuration(6000L);
        img1.setZoomX(10000);
        img1.setZoomY(10000);
        img1.setPositionX(0);
        img1.setPositionY(0);
        callApi("/api/project/image", img1, "2. 添加图片1成功");

        // 3. 添加图片2 (6-12s)
        AddImageRequest img2 = new AddImageRequest();
        img2.setProjectId(projectId);
        img2.setScriptIndex(0);
        img2.setImageId(100102L);
        img2.setImageUrl("file:///root/dreamX/doc/sale/2.png");
        img2.setStartTime(6000L);
        img2.setDuration(6000L);
        img2.setZoomX(10000);
        img2.setZoomY(10000);
        img2.setPositionX(0);
        img2.setPositionY(0);
        callApi("/api/project/image", img2, "3. 添加图片2成功");

        // 4. 添加图片3 (12-18s)
        AddImageRequest img3 = new AddImageRequest();
        img3.setProjectId(projectId);
        img3.setScriptIndex(0);
        img3.setImageId(100103L);
        img3.setImageUrl("file:///root/dreamX/doc/sale/3.png");
        img3.setStartTime(12000L);
        img3.setDuration(6000L);
        img3.setZoomX(10000);
        img3.setZoomY(10000);
        img3.setPositionX(0);
        img3.setPositionY(0);
        callApi("/api/project/image", img3, "4. 添加图片3成功");

        // 5. 添加图片4 (18-24s)
        AddImageRequest img4 = new AddImageRequest();
        img4.setProjectId(projectId);
        img4.setScriptIndex(0);
        img4.setImageId(100104L);
        img4.setImageUrl("file:///root/dreamX/doc/sale/4.png");
        img4.setStartTime(18000L);
        img4.setDuration(6000L);
        img4.setZoomX(10000);
        img4.setZoomY(10000);
        img4.setPositionX(0);
        img4.setPositionY(0);
        callApi("/api/project/image", img4, "5. 添加图片4成功");

        // 6. 添加音频 (0-24s)
        AddAudioRequest audio = new AddAudioRequest();
        audio.setProjectId(projectId);
        audio.setScriptIndex(0);
        audio.setAudioId(100201L);
        audio.setAudioUrl("file:///root/dreamX/doc/sale/535010997887571025.mp3");
        audio.setStartTime(0L);
        audio.setDuration(24000L);
        audio.setMaterialTimeStart(0L);
        audio.setMaterialTimeEnd(127500L);
        audio.setVolume(-30);
        callApi("/api/project/audio", audio, "6. 添加音频成功");

        // 7-10. 添加字幕文本
        addSubtitle(projectId, "千问砸30亿请全国喝奶茶！", 0L, 6000L, "#FFFFFF", "7. 添加字幕1成功");
        addSubtitle(projectId, "结果用户太多 APP直接崩了！", 6000L, 6000L, "#FFFFFF", "8. 添加字幕2成功");
        addSubtitle(projectId, "打工人在网上已经炸锅了", 12000L, 6000L, "#FFFFFF", "9. 添加字幕3成功");
        addSubtitle(projectId, "想看第一手瓜？打开脉脉搜千问！", 18000L, 6000L, "#FFD700", "10. 添加字幕4成功");

        // 11. 构建工程
        BuildProjectRequest buildReq = new BuildProjectRequest();
        buildReq.setProjectId(projectId);
        buildReq.setVideoId(projectId);

        MvcResult buildResult = mockMvc.perform(post("/api/project/build")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(JsonUtils.toJsonString(buildReq)))
                .andExpect(status().isOk())
                .andReturn();
        BaseResponse<Long> buildResp = JsonUtils.toObject(buildResult.getResponse().getContentAsString(), new TypeReference<>() {});
        assertEquals(0, buildResp.getCode());
        assertNotNull(buildResp.getData());
        System.out.println("11. 构建成功, taskId: " + buildResp.getData());

        // 12. 读取任务文件获取 COS URL
        long taskId = buildResp.getData();
        java.io.File taskFile = new java.io.File("tmp/task_0/" + taskId + ".json");
        if (taskFile.exists()) {
            String taskJson = new String(java.nio.file.Files.readAllBytes(taskFile.toPath()));
            System.out.println("=== 任务详情 ===");
            System.out.println(taskJson);
        }
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
                .setFontSize(12)
                .setBold(true)
                .setTextAlign(1)
                .setFontName("抖音美好体")
                .setFillColor(fillColor)
                .setStrokeColor("#000000")
                .setStrokeWidth(8));
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
