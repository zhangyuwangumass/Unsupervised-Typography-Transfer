# -*- coding: utf-8 -*-


import tensorflow as tf
import argparse

from model.zi2ziNet.unet import UNet

parser = argparse.ArgumentParser(description='Train')
# parser.add_argument('--src_font', dest='src_font', required=True, help='path of the source font')
parser.add_argument('--dst_font', dest='dst_font', default='fonts/NotoSerifCJK.ttc', help='path of the target font')
parser.add_argument('--text', dest='text', default=None)
parser.add_argument('--checkpoint', dest='checkpoint')
parser.add_argument('--prepare', dest='prepare', action='store_true', default=False)
parser.add_argument('--infer', dest='infer', action='store_true', default=False)


args = parser.parse_args()


def inspect_graph():
    from pprint import pprint
    var_list = tf.global_variables()
    collection_list = tf.get_default_graph().get_all_collection_keys()
    pprint(var_list)
    pprint(tf.get_default_graph().get_tensor_by_name("no_target_A_and_B_images:0"))


from subprocess import call


def main(_):
    config = tf.ConfigProto()
    with open("./infer_charset", "w") as f:
        if args.text:
            f.write(args.text)
        f.write("南去經三國，東來過五湖。")
        f.write("︽永東國酬愛鬱靈鷹袋︾")
        f.write("あのイーハトーヴォのすきとおった風、夏でも底に冷たさをもつ青いそら、うつくしい森で飾られたモーリオ市、郊外のぎらぎらひかる草の波。")
        f.write("동해물과、백두산이、마르고닳도록、하느님이、보우하사。")
        f.write("ABCDEFGHIJKLM")
        f.write("\n")

    if args.prepare:
        call(
            "rm -rf zi2ziu_infer_sample && mkdir -p zi2ziu_infer_sample && mkdir inferred",
            shell=True)
        call(
            "python3 font2img.py --src_font fonts/NotoSansCJK.ttc --dst_font %s --sample_dir zi2ziu_infer_sample --mode L  --charset infer_charset"%args.dst_font,
            shell=True)

        call(
            "python3 img2pickle.py --dir zi2ziu_infer_sample --save_dir zi2ziu_infer_sample --split_ratio 1",
            shell=True
        )

    if args.infer:
        if args.checkpoint is None:
            print("Need to assign a checkpoint file! Failed")
            return
        with tf.Session(config=config) as sess:
            model = UNet(batch_size=9)
            model.register_session(sess)
            model.build_model(is_training=True)
            tf.global_variables_initializer().run()
            model.infer(source_obj="./zi2ziu_infer_sample/val.obj", model_dir=args.checkpoint,
                        embedding_ids=[0], save_dir="./inferred/", char_num_x=16, char_num_y=9)
    print("Done")


if __name__ == '__main__':
    tf.app.run()
