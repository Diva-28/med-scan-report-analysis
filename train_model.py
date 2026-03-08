import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
import matplotlib.pyplot as plt

# Paths
TRAIN_DIR = 'data/Training'
MODEL_NAME = 'brain_tumor_model.h5'

# Parameters
IMG_SIZE = (224, 224)
BATCH_SIZE = 32

# ❗ HEAVY augmentation to handle side-views (Sagittal) and top-views (Axial)
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=90,     # Extreme rotation for different scan angles
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.3,
    horizontal_flip=True,
    vertical_flip=True,    # Crucial for non-standard scan orientations
    brightness_range=[0.7, 1.3],
    fill_mode='nearest',
    validation_split=0.2
)

train_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training',
    shuffle=True
)

val_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation'
)

# VERIFY CLASS MAPPING
print("Class Indices:", train_generator.class_indices)

# Build Model
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(512, activation='relu')(x)
x = Dropout(0.5)(x)  # Increased dropout for better generalization
x = Dense(256, activation='relu')(x)
x = Dropout(0.3)(x)
predictions = Dense(4, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=predictions)

# Callbacks
checkpoint = ModelCheckpoint(MODEL_NAME, monitor='val_accuracy', save_best_only=True, mode='max', verbose=1)
early_stop = EarlyStopping(monitor='val_loss', patience=8, restore_best_weights=True)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, min_lr=1e-6)

# Phase 1: Rapid training of top layers
print("Phase 1: Training classifier...")
model.compile(optimizer=Adam(learning_rate=0.001), loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(train_generator, epochs=12, validation_data=val_generator, callbacks=[checkpoint, early_stop, reduce_lr])

# Phase 2: Deep Fine-tuning
print("Phase 2: Deep Fine-tuning...")
base_model.trainable = True
# Freeze fewer layers (allow deeper specialization)
for layer in base_model.layers[:80]:
    layer.trainable = False

model.compile(optimizer=Adam(learning_rate=0.00005), loss='categorical_crossentropy', metrics=['accuracy'])
history = model.fit(train_generator, epochs=15, validation_data=val_generator, callbacks=[checkpoint, early_stop, reduce_lr])

print(f"Final Model saved/updated as {MODEL_NAME}")

# Plot results
plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='train_acc')
plt.plot(history.history['val_accuracy'], label='val_acc')
plt.legend()
plt.title('Accuracy (Fine-tuning)')
plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='train_loss')
plt.plot(history.history['val_loss'], label='val_loss')
plt.legend()
plt.title('Loss (Fine-tuning)')
plt.savefig('training_results.png')
print("Plots updated.")


