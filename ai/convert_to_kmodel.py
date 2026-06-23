"""
ONNX to KModel 转换脚本
用于将 YOLO 模型转换为 K230 平台的 kmodel 格式

使用方法:
    python convert_to_kmodel.py --model path/to/best.onnx
    python convert_to_kmodel.py --model path/to/best.onnx --ptq_option 1 --dataset path/to/calibration/images
"""

import argparse
import onnx
import os
from nncase import CompileOptions, Compiler, ImportOptions, ModelQuantMode


def main():
    # 1. 解析参数
    parser = argparse.ArgumentParser(description='YOLOv11 ONNX to K230 KModel (nncase 1.x)')
    parser.add_argument('--model', type=str, required=True,
                        help='ONNX model path (e.g., silkworm_project/health_detect/weights/best.onnx)')
    parser.add_argument('--target', type=str, default='k230', help='Target platform')
    parser.add_argument('--input_width', type=int, default=640, help='Input width')
    parser.add_argument('--input_height', type=int, default=640, help='Input height')
    parser.add_argument('--input_range', type=str, default='0,255', help='Input range (0,255)')
    parser.add_argument('--ptq_option', type=int, default=0, help='0: disable PTQ, 1: enable')
    parser.add_argument('--dataset', type=str, default=None,
                        help='PTQ calibration dataset path (required if ptq_option=1)')

    args = parser.parse_args()

    # 2. 验证 ONNX 模型
    try:
        model = onnx.load(args.model)
        input_tensor = model.graph.input[0]
        input_name = input_tensor.name
        input_shape = [dim.dim_value for dim in input_tensor.type.tensor_type.shape.dim]
        print(f"[OK] Model loaded:")
        print(f"     Input name: {input_name}")
        print(f"     Input shape: {input_shape}")
    except Exception as e:
        print(f"[ERROR] Model load failed: {e}")
        return

    # 3. 解析输入范围
    try:
        input_range = list(map(float, args.input_range.split(',')))
        if len(input_range) != 2:
            raise ValueError("input_range must be two values, e.g., 0,255")
    except Exception as e:
        print(f"[WARN] input_range parse failed: {e}, using default [0.0, 255.0]")
        input_range = [0.0, 255.0]

    # 4. 配置编译选项
    compile_opts = CompileOptions()
    compile_opts.target = args.target
    compile_opts.dump_ir = False
    compile_opts.dump_asm = False

    # 5. 配置导入选项
    import_opts = ImportOptions()
    import_opts.input_range = {input_name: input_range}
    import_opts.input_shape = {input_name: [1, 3, args.input_height, args.input_width]}

    # 6. PTQ 量化配置
    if args.ptq_option == 1:
        if not args.dataset or not os.path.exists(args.dataset):
            print("[ERROR] PTQ dataset not found. Please provide --dataset path")
            return
        compile_opts.ptq_dataset = args.dataset
        compile_opts.ptq_calibration_samples = 50
        compile_opts.quant_mode = ModelQuantMode.QInt8
        print(f"[OK] PTQ enabled, calibration dataset: {args.dataset}")

    # 7. 编译模型
    try:
        compiler = Compiler(compile_opts)
        compiler.import_onnx(args.model, import_opts)
        compiler.compile()
        kmodel = compiler.gencode_to_bytes()

        # 8. 保存 KModel 文件
        output_path = args.model.replace('.onnx', '.kmodel')
        with open(output_path, 'wb') as f:
            f.write(kmodel)
        print(f"[OK] KModel exported:")
        print(f"     Output: {output_path}")
        print(f"     Size: {len(kmodel) / 1024:.1f} KB")
    except AttributeError as e:
        print(f"[WARN] import_onnx not available, trying fallback: {e}")
        try:
            from nncase import compile_model
            kmodel = compile_model(args.model, compile_opts)
            output_path = args.model.replace('.onnx', '.kmodel')
            with open(output_path, 'wb') as f:
                f.write(kmodel)
            print(f"[OK] KModel exported (fallback): {output_path}")
        except Exception as e2:
            print(f"[ERROR] Fallback also failed: {e2}")
    except Exception as e:
        print(f"[ERROR] Compile failed: {e}")


if __name__ == '__main__':
    main()
