# HomeAssistant 天气卡

## 效果图

![图](https://github.com/morestart/weather/blob/master/view.png)


## 使用方法：

- 在HA中建立以下路径`home assistant\custom_components\he_weather\weather.py`
- 或者使用此命令下载 `curl -O https://raw.githubusercontent.com/morestart/weather/master/weather.py`

如果HA中不存在以上路径，自行建立即可。

## 配置内容如下

```yaml
weather:
  - platform: he_weather
    api_key: key
    id: auto_ip 或者 填写城市名称 eg（北京，beijing）
```

## 天气卡片美化

感谢![kalkih](https://github.com/kalkih/simple-weather-card)贡献

效果图:

![](https://github.com/morestart/Weather/blob/master/beautiful.png)

使用方式如下:

- 将`simple-weather-card.bundle.js`文件放置于`\www`文件夹下
  - 使用以下命令下载或者拉取代码包
    - `curl -O https://raw.githubusercontent.com/morestart/Weather/master/simple-weather-card.bundle.js`

配置:

```yaml
cards:
      - type: 'custom:simple-weather-card'
        entity: weather.qing_dao
        name: ' '
        backdrop: true
      - type: 'custom:simple-weather-card'
        entity: weather.qing_dao
        name: 青岛
        backdrop:
          day: var(--primary-color)
          night: '#40445a'
      - type: 'custom:simple-weather-card'
        entity: weather.qing_dao
        name: 青岛
      - entity: weather.qing_dao
        type: weather-forecast
```



