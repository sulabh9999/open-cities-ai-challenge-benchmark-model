# tiny_spacenet.py

import rastervision as rv

class TinySpacenetExperimentSet(rv.ExperimentSet):
    def exp_main(self):
        base_uri = ('https://s3.amazonaws.com/azavea-research-public-data/'
                    'raster-vision/examples/spacenet')
        train_image_uri = '{}/RGB-PanSharpen_AOI_2_Vegas_img205.tif'.format(base_uri)
        train_label_uri = '{}/buildings_AOI_2_Vegas_img205.geojson'.format(base_uri)
        val_image_uri = '{}/RGB-PanSharpen_AOI_2_Vegas_img25.tif'.format(base_uri)
        val_label_uri = '{}/buildings_AOI_2_Vegas_img25.geojson'.format(base_uri)
        channel_order = [0, 1, 2]
        background_class_id = 2

        # ------------- TASK -------------

        task = rv.TaskConfig.builder(rv.SEMANTIC_SEGMENTATION) \
                            .with_chip_size(300) \
                            .with_chip_options(chips_per_scene=50) \
                            .with_classes({
                                'building': (1, 'red'),
                                'background': (2, 'black')
                            }) \
                            .build()

        # ------------- BACKEND -------------

        backend = rv.BackendConfig.builder(rv.PYTORCH_SEMANTIC_SEGMENTATION) \
            .with_task(task) \
            .with_train_options(
                batch_size=2,
                num_epochs=1,
                debug=True) \
            .build()

        # ------------- TRAINING -------------

        train_raster_source = rv.RasterSourceConfig.builder(rv.RASTERIO_SOURCE) \
                                                   .with_uri(train_image_uri) \
                                                   .with_channel_order(channel_order) \
                                                   .with_stats_transformer() \
                                                   .build()

        train_label_raster_source = rv.RasterSourceConfig.builder(rv.RASTERIZED_SOURCE) \
                                                         .with_vector_source(train_label_uri) \
                                                         .with_rasterizer_options(background_class_id) \
                                                         .build()
        train_label_source = rv.LabelSourceConfig.builder(rv.SEMANTIC_SEGMENTATION) \
                                                 .with_raster_source(train_label_raster_source) \
                                                 .build()

        train_scene =  rv.SceneConfig.builder() \
                                     .with_task(task) \
                                     .with_id('train_scene') \
                                     .with_raster_source(train_raster_source) \
                                     .with_label_source(train_label_source) \
                                     .build()

        # ------------- VALIDATION -------------

        val_raster_source = rv.RasterSourceConfig.builder(rv.RASTERIO_SOURCE) \
                                                 .with_uri(val_image_uri) \
                                                 .with_channel_order(channel_order) \
                                                 .with_stats_transformer() \
                                                 .build()

        val_label_raster_source = rv.RasterSourceConfig.builder(rv.RASTERIZED_SOURCE) \
                                                       .with_vector_source(val_label_uri) \
                                                       .with_rasterizer_options(background_class_id) \
                                                       .build()
        val_label_source = rv.LabelSourceConfig.builder(rv.SEMANTIC_SEGMENTATION) \
                                               .with_raster_source(val_label_raster_source) \
                                               .build()

        val_scene = rv.SceneConfig.builder() \
                                  .with_task(task) \
                                  .with_id('val_scene') \
                                  .with_raster_source(val_raster_source) \
                                  .with_label_source(val_label_source) \
                                  .build()

        # ------------- DATASET -------------

        dataset = rv.DatasetConfig.builder() \
                                  .with_train_scene(train_scene) \
                                  .with_validation_scene(val_scene) \
                                  .build()

        # ------------- EXPERIMENT -------------

        experiment = rv.ExperimentConfig.builder() \
                                        .with_id('tiny-spacenet-experiment') \
                                        .with_root_uri('/opt/data/rv') \
                                        .with_task(task) \
                                        .with_backend(backend) \
                                        .with_dataset(dataset) \
                                        .with_stats_analyzer() \
                                        .build()

        return experiment


if __name__ == '__main__':
    rv.main()