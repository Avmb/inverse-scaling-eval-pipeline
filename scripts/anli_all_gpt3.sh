SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source $SCRIPT_DIR/../.venv/bin/activate

EXP_DIR=anli_all-gpt3
python $SCRIPT_DIR/../eval_pipeline/main.py \
    --dataset anli_all \
    --exp-dir $EXP_DIR \
    --models ada babbage curie davinci \
    --batch-size 50 \
&& \
python $SCRIPT_DIR/../eval_pipeline/plot_loss.py \
    $EXP_DIR


