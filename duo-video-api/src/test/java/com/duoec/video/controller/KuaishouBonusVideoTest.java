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
class KuaishouBonusVideoTest {
    static {
        JianyingBuilder.storageService = new StorageServiceImpl();
        JianyingProjectBuildState.DEBUG_JY_DRAFT_DIR = "/root/dreamX/tmp/jy-drafts/";
    }

    @Autowired
    private MockMvc mockMvc;

    @Test
    void testBuildKuaishouBonusVideo() throws Exception {
        long projectId = 200001L;

        // 1. 创建项目
        CreateProjectRequest createReq = new CreateProjectRequest();
        createReq.setProjectId(projectId);
        createReq.setProjectName("快手年终奖_脉脉营销");
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

        // 2. 添加图片1 (0-5s)
        addImage(projectId, 200101L, "file:///root/dreamX/doc/sale/kuaishou_bonus/1.jpg", 0L, 5000L, "2. 添加图片1成功");

        // 3. 添加图片2 (5-10s)
        addImage(projectId, 200102L, "file:///root/dreamX/doc/sale/kuaishou_bonus/2.jpg", 5000L, 5000L, "3. 添加图片2成功");

        // 4. 添加图片3 (10-15s)
        addImage(projectId, 200103L, "file:///root/dreamX/doc/sale/kuaishou_bonus/3.jpg", 10000L, 5000L, "4. 添加图片3成功");

        // 5. 添加图片4 (15-20s)
        addImage(projectId, 200104L, "file:///root/dreamX/doc/sale/kuaishou_bonus/4.jpg", 15000L, 5000L, "5. 添加图片4成功");

        // 6. 添加图片5 (20-25s)
        addImage(projectId, 200105L, "file:///root/dreamX/doc/sale/kuaishou_bonus/5.jpg", 20000L, 5000L, "6. 添加图片5成功");

        // 7. 添加音频 (0-25s)
        AddAudioRequest audio = new AddAudioRequest();
        audio.setProjectId(projectId);
        audio.setScriptIndex(0);
        audio.setAudioId(200201L);
        audio.setAudioUrl("file:///root/dreamX/doc/sale/535010997887571025.mp3");
        audio.setStartTime(0L);
        audio.setDuration(25000L);
        audio.setMaterialTimeStart(0L);
        audio.setMaterialTimeEnd(127500L);
        audio.setVolume(-30);
        callApi("/api/project/audio", audio, "7. 添加音频成功");

        // 8-12. 添加字幕
        addSubtitle(projectId, "快手年终奖开奖了！发的真多！", 0L, 5000L, "#FFFFFF", "8. 添加字幕1成功");
        addSubtitle(projectId, "打工人直呼羡慕哭了", 5000L, 5000L, "#FFFFFF", "9. 添加字幕2成功");
        addSubtitle(projectId, "脉脉上已经炸锅了", 10000L, 5000L, "#FFFFFF", "10. 添加字幕3成功");
        addSubtitle(projectId, "评论区比春晚还热闹", 15000L, 5000L, "#FFFFFF", "11. 添加字幕4成功");
        addSubtitle(projectId, "想看第一手瓜？打开脉脉搜快手！", 20000L, 5000L, "#FFD700", "12. 添加字幕5成功");

        // 13. 构建工程
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
        System.out.println("13. 构建成功, taskId: " + buildResp.getData());

        // 14. 读取任务文件获取 COS URL
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
