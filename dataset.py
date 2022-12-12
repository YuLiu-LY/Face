import os
import sys
root_path = os.path.abspath(__file__)
root_path = '/'.join(root_path.split('/')[:-2])
sys.path.append(root_path)

import torch
import random
from PIL import Image
from glob import glob
import pytorch_lightning as pl
from torch.utils.data import DataLoader, Dataset
from torchvision.transforms import transforms


class FaceDataset(Dataset):
    def __init__(
        self,
        data_root: str,
        split:str,
    ):
        super().__init__()
        self.data_root = data_root
        self.split = split

        self.get_files()

        self.T1 = transforms.ToTensor()
        self.T2 = transforms.Compose([
            transforms.RandomGrayscale(0.1),
            transforms.RandomHorizontalFlip(1),
            transforms.ToTensor(),
        ])
        
    def __getitem__(self, index: int):
        img_paths = self.img_files[index]
        if len(img_paths) < 2:
            img1 = Image.open(img_paths[0]).convert("RGB")
            img_pair= [self.T1(img1), self.T2(img1)]
        else:
            random.shuffle(img_paths)
            img1 = Image.open(img_paths[0]).convert("RGB")
            img2 = Image.open(img_paths[1]).convert("RGB")
            img_pair = [self.T1(img1), self.T1(img2)]
        img_pair = torch.stack(img_pair, dim=0)
        return {'image': img_pair}


    def __len__(self):
        return len(self.img_files)
    
    def get_files(self):
        with open(f'{self.data_root}/{self.split}.txt', 'r') as f:
            img_dirs = f.read().splitlines()
        self.img_files = [sorted(glob(f'{dir}/*_a.jpg')) for dir in img_dirs]
              

class FaceDataModule(pl.LightningDataModule):
    def __init__(
        self,
        args,
    ):
        super().__init__()
        self.batch_size = args.batch_size
        self.num_workers = args.num_workers

        self.train_dataset = FaceDataset(args.data_root, 'train')
        self.val_dataset = FaceDataset(args.data_root, 'val')
        self.test_dataset = FaceDataset(args.data_root, 'test')

    def train_dataloader(self):
        return DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.num_workers,
            pin_memory=True,
        )

    def val_dataloader(self):
        return DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=True,
        )
    
    def test_dataloader(self):
        return DataLoader(
            self.test_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=True,
        )


'''test'''
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    args.data_root = '/Users/liuyu/Downloads/Face'
    args.use_rescale = False
    args.batch_size = 20
    args.num_workers = 4

    datamodule = FaceDataModule(args)
    dl = datamodule.val_dataloader()
    it = iter(dl)
    batch = next(it)
    print(batch['image'].shape)
    
