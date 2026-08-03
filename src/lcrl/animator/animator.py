import os
import matplotlib.pyplot as plt
import numpy as np
import tqdm
import imageio.v2 as imageio
from lcrl.environments.SlipperyGrid import SlipperyGrid


def animate(mdp, executed_policy, dir_to_save, labels_value, cmap, norm, patches):
    if isinstance(mdp, SlipperyGrid):
        animation_dir = os.path.join(dir_to_save, 'animation')
        if not os.path.exists(animation_dir):
            os.mkdir(animation_dir)
        for file_name in os.listdir(animation_dir):
            if file_name.startswith('image_file_') and file_name.endswith('.png'):
                os.remove(os.path.join(animation_dir, file_name))
        print('---------------------------------\n')
        print('Creating a gif for the trained policy:')
        for i in tqdm.tqdm(range(len(executed_policy))):
            fig, ax = plt.subplots()
            ax.imshow(labels_value, interpolation='nearest', cmap=cmap, norm=norm)
            ax.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
            initial_x = executed_policy[0][0]
            initial_y = executed_policy[0][1]
            if i == 0:
                path_x, path_y = executed_policy[0]
                ax.scatter(path_y, path_x, c='red', edgecolors='darkred')
            else:
                traversed_path = np.array(executed_policy[0:i])
                path_x, path_y = traversed_path.T
                ax.scatter(path_y, path_x, c='lime', edgecolors='teal')
                current_x, current_y = executed_policy[i]
                ax.scatter(current_y, current_x, c='red', edgecolors='darkred')
            ax.annotate('s_0', (initial_y, initial_x), fontsize=15, xytext=(20, 20), textcoords="offset points",
                        va="center", ha="left",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
            ax.set_title('This policy is synthesised by the trained agent')
            fig.savefig(os.path.join(animation_dir, 'image_file_' + str(i) + '.png'), bbox_inches="tight")
            plt.close(fig)
        images = []
        frame_files = sorted(
            [
                file_name for file_name in os.listdir(animation_dir)
                if file_name.startswith('image_file_') and file_name.endswith('.png')
            ],
            key=lambda file_name: int(file_name.rsplit('_', 1)[1].split('.')[0])
        )
        for file_name in frame_files:
            file_path = os.path.join(animation_dir, file_name)
            images.append(imageio.imread(file_path))
        imageio.mimsave(os.path.join(animation_dir, 'executed_policy.gif'), images, fps=55)
    else:
        raise NotImplementedError('The animator does not support this environment yet.')
